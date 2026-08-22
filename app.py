
import os
import uuid
import requests
from flask import Flask, render_template, request, jsonify, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager
from config import Config
from utils.database import db

# Initialize extensions
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
jwt = JWTManager()

from utils.websocket_handler import BackgroundTasks

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize plugins
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)
    
    # Start background tasks
    bg_tasks = BackgroundTasks(socketio, app)
    bg_tasks.start()
    
    # Register blueprints (to be created)
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(scanner_bp, url_prefix='/api/scanner')
    
    # Setup database
    with app.app_context():
        db.create_all()
        # Seed dummy user for hackathon testing
        from utils.database import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='demo').first():
            demo_user = User(
                username='demo',
                email='demo@Krishi Drishti.com',
                password_hash=generate_password_hash('password123'),
                full_name='Demo Farmer',
                role='farmer'
            )
            db.session.add(demo_user)
            db.session.commit()
        # Seed store products
        try:
            from utils.store_data import seed_store_data
            seed_store_data()
        except Exception as e:
            print(f'Store seed error: {e}')
    
    # Authentication Routes
    @app.route('/', methods=['GET'])
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login_post():
        username = request.form.get('username')
        password = request.form.get('password')
        
        from utils.database import User
        
        users = User.query.all()
        logged_in_user = None
        for u in users:
            if check_password_hash(u.password_hash, password):
                logged_in_user = u
                break
                
        if logged_in_user:
            session['user_id'] = logged_in_user.id
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password')
            return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            from utils.database import User
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
                
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.')
            return redirect(url_for('index'))
            
        return render_template('register.html')
        
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            flash('A password reset link has been sent to your email (simulated).')
            return redirect(url_for('index'))
        return render_template('forgot_password.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    # Dashboard Routes (Protected)
    @app.before_request
    def require_login():
        allowed_routes = ['index', 'login_post', 'register', 'forgot_password', 'static']
        if request.endpoint not in allowed_routes and 'user_id' not in session:
            # We don't block API or socketio for this demo, but we should block HTML views
            if request.endpoint and not request.endpoint.startswith('api_'):
                return redirect(url_for('index'))
                
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/scanner')
    def scanner():
        return render_template('scanner.html')

    @app.route('/weather')
    def weather():
        return render_template('weather_map.html')

    @app.route('/recommendations')
    def recommendations():
        return render_template('recommendations.html')

    @app.route('/field_map')
    def field_map():
        return render_template('weather_map.html')

    @app.route('/alerts')
    def alerts():
        from utils.database import Alert
        user_id = session.get('user_id')
        db_alerts = Alert.query.filter_by(user_id=user_id).order_by(Alert.created_at.desc()).all() if user_id else []
        return render_template('alerts.html', db_alerts=db_alerts)

    @app.route('/yojanas')
    def yojanas():
        return render_template('yojanas.html')

    @app.route('/yield_prediction')
    def yield_prediction():
        return render_template('yield_prediction.html')

    @app.route('/irrigation')
    def irrigation():
        return render_template('irrigation.html')

    @app.route('/profile')
    def profile():
        return render_template('profile.html')
        
    @app.route('/settings')
    def settings():
        return render_template('settings.html')
        
    @app.route('/store')
    def store():
        from utils.database import Product
        search = request.args.get('q', '')
        category = request.args.get('category', 'all')
        products = Product.query
        if search:
            products = products.filter(Product.name.ilike(f'%{search}%'))
        if category != 'all':
            products = products.filter_by(category=category)
        products = products.all()
        return render_template('store.html', products=products, search=search, category=category)

    @app.route('/store/<int:product_id>')
    def product_detail(product_id):
        from utils.database import Product
        product = Product.query.get_or_404(product_id)
        related = Product.query.filter_by(category=product.category).filter(Product.id != product.id).limit(4).all()
        return render_template('product_detail.html', product=product, related=related)

    @app.route('/map')
    def agri_map():
        return render_template('weather_map.html')

    @app.route('/mandi')
    def mandi():
        # Mock Mandi rates data for Hackathon demo
        import datetime
        today = datetime.date.today().strftime('%d %b %Y')
        mock_rates = [
            {'state': 'Punjab', 'market': 'Amritsar', 'commodity': 'Wheat', 'variety': 'Other', 'date': today, 'min_price': '2200', 'max_price': '2350', 'modal_price': '2275'},
            {'state': 'Maharashtra', 'market': 'Pune', 'commodity': 'Onion', 'variety': 'Red', 'date': today, 'min_price': '1500', 'max_price': '2100', 'modal_price': '1800'},
            {'state': 'Punjab', 'market': 'Ludhiana', 'commodity': 'Rice', 'variety': 'Basmati', 'date': today, 'min_price': '3500', 'max_price': '4200', 'modal_price': '3800'},
            {'state': 'Haryana', 'market': 'Karnal', 'commodity': 'Cotton', 'variety': 'Desi', 'date': today, 'min_price': '6500', 'max_price': '7200', 'modal_price': '6800'},
            {'state': 'UP', 'market': 'Meerut', 'commodity': 'Sugarcane', 'variety': 'Normal', 'date': today, 'min_price': '300', 'max_price': '350', 'modal_price': '340'},
            {'state': 'MP', 'market': 'Indore', 'commodity': 'Soyabean', 'variety': 'Yellow', 'date': today, 'min_price': '4200', 'max_price': '4600', 'modal_price': '4450'},
            {'state': 'Gujarat', 'market': 'Rajkot', 'commodity': 'Groundnut', 'variety': 'Bold', 'date': today, 'min_price': '5200', 'max_price': '5800', 'modal_price': '5500'},
            {'state': 'Rajasthan', 'market': 'Jaipur', 'commodity': 'Mustard', 'variety': 'Black', 'date': today, 'min_price': '4800', 'max_price': '5100', 'modal_price': '4950'},
            {'state': 'Karnataka', 'market': 'Bangalore', 'commodity': 'Tomato', 'variety': 'Local', 'date': today, 'min_price': '800', 'max_price': '1200', 'modal_price': '1000'},
            {'state': 'AP', 'market': 'Guntur', 'commodity': 'Chilli', 'variety': 'Red', 'date': today, 'min_price': '15000', 'max_price': '18000', 'modal_price': '16500'},
            {'state': 'Tamil Nadu', 'market': 'Erode', 'commodity': 'Turmeric', 'variety': 'Bulb', 'date': today, 'min_price': '7000', 'max_price': '8200', 'modal_price': '7600'},
            {'state': 'Kerala', 'market': 'Kochi', 'commodity': 'Coconut', 'variety': 'Dry', 'date': today, 'min_price': '3000', 'max_price': '3500', 'modal_price': '3250'},
            {'state': 'West Bengal', 'market': 'Burdwan', 'commodity': 'Potato', 'variety': 'Jyoti', 'date': today, 'min_price': '1100', 'max_price': '1400', 'modal_price': '1250'},
            {'state': 'Bihar', 'market': 'Patna', 'commodity': 'Maize', 'variety': 'Yellow', 'date': today, 'min_price': '2100', 'max_price': '2300', 'modal_price': '2200'},
            {'state': 'Assam', 'market': 'Guwahati', 'commodity': 'Tea', 'variety': 'CTC', 'date': today, 'min_price': '15000', 'max_price': '25000', 'modal_price': '20000'},
            {'state': 'Odisha', 'market': 'Bhubaneswar', 'commodity': 'Brinjal', 'variety': 'Round', 'date': today, 'min_price': '1200', 'max_price': '1600', 'modal_price': '1400'},
            {'state': 'Chhattisgarh', 'market': 'Raipur', 'commodity': 'Paddy', 'variety': 'Common', 'date': today, 'min_price': '2000', 'max_price': '2183', 'modal_price': '2183'},
            {'state': 'Telangana', 'market': 'Warangal', 'commodity': 'Cotton', 'variety': 'Long Staple', 'date': today, 'min_price': '6800', 'max_price': '7400', 'modal_price': '7100'},
            {'state': 'UP', 'market': 'Agra', 'commodity': 'Potato', 'variety': 'Desi', 'date': today, 'min_price': '900', 'max_price': '1200', 'modal_price': '1050'},
            {'state': 'Maharashtra', 'market': 'Nashik', 'commodity': 'Grapes', 'variety': 'Green', 'date': today, 'min_price': '4000', 'max_price': '6000', 'modal_price': '5000'},
            {'state': 'Gujarat', 'market': 'Surat', 'commodity': 'Banana', 'variety': 'Robusta', 'date': today, 'min_price': '1200', 'max_price': '1500', 'modal_price': '1350'},
            {'state': 'MP', 'market': 'Ujjain', 'commodity': 'Garlic', 'variety': 'White', 'date': today, 'min_price': '6000', 'max_price': '9000', 'modal_price': '7500'},
            {'state': 'Karnataka', 'market': 'Mysore', 'commodity': 'Arecanut', 'variety': 'Red', 'date': today, 'min_price': '35000', 'max_price': '42000', 'modal_price': '38000'},
            {'state': 'AP', 'market': 'Vijayawada', 'commodity': 'Mango', 'variety': 'Banganapalli', 'date': today, 'min_price': '2500', 'max_price': '4000', 'modal_price': '3200'}
        ]
        return render_template('mandi.html', rates=mock_rates)
        
    # API Routes
    @app.route('/api/recommend', methods=['POST'])
    def api_recommend():
        data = request.json
        gemini_key = app.config.get('GEMINI_API_KEY')
        if not gemini_key:
            return jsonify({'error': 'Gemini API key is missing'}), 500
            
        try:
            import json
            import urllib.parse
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
            prompt = (
                f"You are an expert agricultural AI with knowledge of over 150 diverse crops. "
                f"Based on the following exact parameters for farming in India, accurately recommend the top 5 most suitable crops:\n"
                f"Nitrogen (N): {data.get('N')} kg/ha\n"
                f"Phosphorus (P): {data.get('P')} kg/ha\n"
                f"Potassium (K): {data.get('K')} kg/ha\n"
                f"Sulfur (S): {data.get('S')} kg/ha\n"
                f"pH: {data.get('ph')}\n"
                f"Temperature: {data.get('temperature')} °C\n"
                f"Humidity: {data.get('humidity')} %\n"
                f"Rainfall: {data.get('rainfall')} mm\n\n"
                f"Return EXACTLY a JSON object with a 'crops' array. Each item in the array must be an object with these exact keys:\n"
                f"- 'name' (string: common English name)\n"
                f"- 'hindi' (string: Hindi name)\n"
                f"- 'tags' (array of 3 short strings, e.g. ['High Water', 'Kharif', 'High ROI'])\n"
                f"- 'yield' (string: expected yield e.g. '40-60 q/ha')\n"
                f"- 'days' (string: duration e.g. '110-150')\n"
                f"- 'msp' (string: MSP or market price estimate)\n"
                f"- 'tip' (string: 1 short actionable farming tip)\n"
                f"- 'probability' (float: confidence score between 0.70 and 0.99)"
            )
            payload = {
                'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0.1, 'responseMimeType': 'application/json'}
            }
            resp = requests.post(url, json=payload, timeout=20)
            resp.raise_for_status()
            resp_data = resp.json()
            text = resp_data['candidates'][0]['content']['parts'][0]['text']
            result = json.loads(text)
            
            # Fetch real wikipedia images dynamically
            for crop in result.get('crops', []):
                crop_name = crop.get('name', '')
                try:
                    wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(crop_name)}&prop=pageimages&format=json&pithumbsize=400"
                    wiki_resp = requests.get(wiki_url, timeout=3).json()
                    pages = wiki_resp.get('query', {}).get('pages', {})
                    img_url = None
                    for page_id, page_info in pages.items():
                        if 'thumbnail' in page_info:
                            img_url = page_info['thumbnail']['source']
                            break
                    crop['img'] = img_url if img_url else f"https://source.unsplash.com/400x300/?{urllib.parse.quote(crop_name)},crop"
                except:
                    crop['img'] = '/static/images/crops/wheat.jpg'
                    
            return jsonify(result)
        except Exception as e:
            print(f'Gemini recommend error: {e}')
            # Advanced ML-like Fallback Engine
            try:
                N = float(data.get('N', 50))
                P = float(data.get('P', 50))
                K = float(data.get('K', 50))
                S = float(data.get('S', 20))
                ph = float(data.get('ph', 6.5))
                temp = float(data.get('temperature', 25))
                rain = float(data.get('rainfall', 100))
            except:
                N, P, K, S, ph, temp, rain = 50, 50, 50, 20, 6.5, 25, 100

            crop_profiles = [
                {"name": "Rice", "hindi": "चावल", "img": "/static/images/crops/rice.jpg", "tags": ["High Water", "Kharif"], "yield": "40-60 q/ha", "days": "110-150", "msp": "₹2,183/q", "tip": "Requires flooded fields.", "ideal": {"N": 100, "P": 50, "K": 50, "S": 20, "ph": 6.0, "temp": 28, "rain": 200}},
                {"name": "Sugarcane", "hindi": "गन्ना", "img": "/static/images/crops/sugarcane.jpg", "tags": ["High Water", "Perennial"], "yield": "700-900 q/ha", "days": "300-365", "msp": "₹340/q", "tip": "Ratoon cropping saves input cost.", "ideal": {"N": 150, "P": 80, "K": 80, "S": 40, "ph": 6.5, "temp": 30, "rain": 150}},
                {"name": "Jute", "hindi": "पटसन", "img": "/static/images/crops/jute.jpg", "tags": ["High Water", "Kharif"], "yield": "25-35 q/ha", "days": "100-120", "msp": "₹4,500/q", "tip": "Needs humid climate.", "ideal": {"N": 80, "P": 40, "K": 40, "S": 20, "ph": 6.0, "temp": 30, "rain": 180}},
                {"name": "Pearl Millet", "hindi": "बाजरा", "img": "/static/images/crops/pearl_millet.jpg", "tags": ["Low Water", "Kharif"], "yield": "15-25 q/ha", "days": "80-90", "msp": "₹2,500/q", "tip": "Highly drought tolerant.", "ideal": {"N": 60, "P": 30, "K": 30, "S": 10, "ph": 7.0, "temp": 32, "rain": 40}},
                {"name": "Sorghum", "hindi": "ज्वार", "img": "/static/images/crops/sorghum.jpg", "tags": ["Low Water", "Kharif"], "yield": "20-30 q/ha", "days": "100-115", "msp": "₹3,180/q", "tip": "Good for fodder and grain.", "ideal": {"N": 80, "P": 40, "K": 40, "S": 20, "ph": 6.5, "temp": 30, "rain": 50}},
                {"name": "Moth Bean", "hindi": "मोठ", "img": "/static/images/crops/moth_bean.jpg", "tags": ["Very Low Water", "Zaid"], "yield": "6-10 q/ha", "days": "75-90", "msp": "₹6,500/q", "tip": "Best for arid regions.", "ideal": {"N": 10, "P": 20, "K": 20, "S": 10, "ph": 7.0, "temp": 35, "rain": 30}},
                {"name": "Wheat", "hindi": "गेहूं", "img": "/static/images/crops/wheat.jpg", "tags": ["Medium Water", "Rabi"], "yield": "45-65 q/ha", "days": "110-140", "msp": "₹2,275/q", "tip": "Sow between Nov 15-Dec 15.", "ideal": {"N": 120, "P": 60, "K": 40, "S": 20, "ph": 6.5, "temp": 20, "rain": 80}},
                {"name": "Mustard", "hindi": "सरसों", "img": "/static/images/crops/mustard.jpg", "tags": ["Low Water", "Rabi"], "yield": "12-18 q/ha", "days": "90-120", "msp": "₹5,650/q", "tip": "Tolerates light frost.", "ideal": {"N": 60, "P": 40, "K": 40, "S": 40, "ph": 6.5, "temp": 18, "rain": 60}},
                {"name": "Chickpea", "hindi": "चना", "img": "/static/images/crops/chickpea.jpg", "tags": ["Low Water", "Rabi"], "yield": "12-20 q/ha", "days": "90-120", "msp": "₹5,440/q", "tip": "Excellent for nitrogen fixation.", "ideal": {"N": 20, "P": 40, "K": 20, "S": 20, "ph": 7.0, "temp": 22, "rain": 50}},
                {"name": "Maize", "hindi": "मक्का", "img": "/static/images/crops/maize.jpg", "tags": ["Medium Water", "Kharif"], "yield": "50-80 q/ha", "days": "80-110", "msp": "₹1,870/q", "tip": "Ensure proper drainage.", "ideal": {"N": 120, "P": 60, "K": 40, "S": 20, "ph": 6.5, "temp": 25, "rain": 100}},
                {"name": "Cotton", "hindi": "कपास", "img": "/static/images/crops/cotton.jpg", "tags": ["Medium Water", "Kharif"], "yield": "15-25 q/ha", "days": "160-200", "msp": "₹6,620/q", "tip": "Requires deep black soil.", "ideal": {"N": 120, "P": 60, "K": 60, "S": 30, "ph": 7.0, "temp": 28, "rain": 100}},
                {"name": "Soybean", "hindi": "सोयाबीन", "img": "/static/images/crops/soybean.jpg", "tags": ["Medium Water", "Kharif"], "yield": "18-25 q/ha", "days": "90-110", "msp": "₹4,600/q", "tip": "Good source of protein and oil.", "ideal": {"N": 20, "P": 60, "K": 40, "S": 20, "ph": 6.5, "temp": 25, "rain": 90}}
            ]

            scored_crops = []
            for crop in crop_profiles:
                ideal = crop['ideal']
                # Calculate normalized deviations (lower is better)
                dev_n = abs(N - ideal['N']) / max(ideal['N'], 1)
                dev_p = abs(P - ideal['P']) / max(ideal['P'], 1)
                dev_k = abs(K - ideal['K']) / max(ideal['K'], 1)
                dev_s = abs(S - ideal['S']) / max(ideal['S'], 1)
                dev_ph = abs(ph - ideal['ph']) / max(ideal['ph'], 1) * 2.0  # pH is sensitive
                dev_temp = abs(temp - ideal['temp']) / max(ideal['temp'], 1) * 1.5 # temp is sensitive
                dev_rain = abs(rain - ideal['rain']) / max(ideal['rain'], 1) * 2.0 # rain is critical

                total_dev = dev_n + dev_p + dev_k + dev_s + dev_ph + dev_temp + dev_rain
                
                # Convert deviation to a probability score between 60% and 99%
                prob = max(60.0, 99.0 - (total_dev * 10))
                prob = round(min(99.9, prob), 1)
                
                crop_data = crop.copy()
                del crop_data['ideal']
                crop_data['probability'] = prob / 100.0
                scored_crops.append(crop_data)

            # Sort by highest probability
            scored_crops.sort(key=lambda x: x['probability'], reverse=True)
            return jsonify({'crops': scored_crops[:3]})

    @app.route('/api/scan', methods=['POST'])
    def api_scan():
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        file = request.files['image']
        
        mistral_key = os.getenv('MISTRAL_API_KEY')
        if not mistral_key:
            return jsonify({'error': 'Mistral API key is missing'}), 500
            
        try:
            import base64
            import json
            import requests
            encoded_image = base64.b64encode(file.read()).decode('utf-8')
            mime_type = file.content_type
            
            url = 'https://api.mistral.ai/v1/chat/completions'
            prompt = (
                "Analyze this plant leaf image. Identify the crop and any disease present. "
                "Provide the disease name, confidence level (e.g. 95%), and 3 recommended treatment steps (including specific fertilizer or chemical names). "
                "Output exactly as a flat JSON dictionary with NO nested objects. Use this exact structure: "
                "{\"disease\": \"Corn Rust\", \"confidence\": \"95%\", \"treatment\": [\"Apply Fungicide X\", \"Use Nitrogen fertilizer\", \"...\"]}"
            )
            payload = {
                'model': 'pixtral-12b-2409',
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{encoded_image}'}}
                        ]
                    }
                ],
                'response_format': {'type': 'json_object'},
                'temperature': 0.2
            }
            resp = requests.post(url, headers={'Authorization': f'Bearer {mistral_key}'}, json=payload, timeout=20)
            resp.raise_for_status()
            resp_data = resp.json()
            text = resp_data['choices'][0]['message']['content']
            
            result = json.loads(text)
            
            # Normalize potential nested structures from Mistral
            disease = result.get('disease', 'Unknown Disease')
            if isinstance(disease, dict):
                disease = disease.get('name', str(disease))
                
            confidence = result.get('confidence', 'N/A')
            if isinstance(confidence, dict):
                confidence = confidence.get('score', str(confidence))
                
            treatment = result.get('treatment', [])
            if isinstance(treatment, dict):
                treatment = list(treatment.values())
            elif isinstance(treatment, list):
                treatment = [t.get('instruction', t.get('step', str(t))) if isinstance(t, dict) else str(t) for t in treatment]
                
            # If Mistral wrapped the entire response in a parent key like {"response": {...}}
            if not disease or disease == 'Unknown Disease':
                for val in result.values():
                    if isinstance(val, dict) and 'disease' in val:
                        disease = val.get('disease', disease)
                        confidence = val.get('confidence', confidence)
                        treatment = val.get('treatment', treatment)
                        break

            return jsonify({
                'disease': str(disease),
                'confidence': str(confidence),
                'treatment': treatment
            })
        except Exception as e:
            print(f'Mistral scan error: {e}')
            return jsonify({'error': 'Failed to analyze image'}), 500

    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        data = request.json
        msg = data.get('message', '')
        
        mistral_key = os.getenv('MISTRAL_API_KEY')
        
        if mistral_key:
            try:
                import json
                import requests
                url = 'https://api.mistral.ai/v1/chat/completions'
                system_prompt = (
                    'You are Krishi Drishti, an expert agricultural assistant for Indian farmers. '
                    'You have deep knowledge of crops, soil health, pest management, fertilizers, seeds, '
                    'weather patterns affecting farming, crop diseases, irrigation techniques, and government '
                    'agricultural schemes. Always give practical, actionable advice in simple language. '
                    'If asked about specific pesticides or seeds, provide dosage, usage, and safety info. '
                    'Respond in the same language the user uses (Hindi, English, or regional languages).'
                )
                payload = {
                    'model': 'mistral-large-latest',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': msg}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 1024
                }
                resp = requests.post(url, headers={'Authorization': f'Bearer {mistral_key}'}, json=payload, timeout=15)
                resp.raise_for_status()
                resp_data = resp.json()
                reply = resp_data['choices'][0]['message']['content']
                return jsonify({'reply': reply, 'powered_by': 'mistral'})
            except Exception as e:
                print(f'Mistral API error: {e}')
                return jsonify({'reply': 'Sorry, I am having trouble connecting to my AI brain right now.', 'powered_by': 'error'}), 500
        else:
            return jsonify({'reply': 'My Mistral API key is missing. Please configure it.', 'powered_by': 'error'}), 500

    # Cart API Routes
    @app.route('/api/cart', methods=['GET'])
    def api_cart_get():
        from utils.database import CartItem
        sess_id = session.get('cart_session_id')
        if not sess_id:
            return jsonify({'items': [], 'total': 0, 'count': 0})
        items = CartItem.query.filter_by(session_id=sess_id).all()
        cart_data = []
        total = 0
        for item in items:
            p = item.product
            subtotal = p.price * item.quantity
            total += subtotal
            cart_data.append({
                'id': item.id,
                'product_id': p.id,
                'name': p.name,
                'brand': p.brand,
                'price': p.price,
                'quantity': item.quantity,
                'unit': p.unit,
                'image_url': p.image_url,
                'subtotal': subtotal
            })
        return jsonify({'items': cart_data, 'total': total, 'count': len(cart_data)})

    @app.route('/api/cart/add', methods=['POST'])
    def api_cart_add():
        from utils.database import CartItem, Product
        data = request.json
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if 'cart_session_id' not in session:
            session['cart_session_id'] = str(uuid.uuid4())
        sess_id = session['cart_session_id']
        
        existing = CartItem.query.filter_by(session_id=sess_id, product_id=product_id).first()
        if existing:
            existing.quantity += quantity
        else:
            cart_item = CartItem(session_id=sess_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
        
        count = CartItem.query.filter_by(session_id=sess_id).count()
        return jsonify({'success': True, 'message': f'{product.name} added to cart!', 'cart_count': count})

    @app.route('/api/cart/remove', methods=['POST'])
    def api_cart_remove():
        from utils.database import CartItem
        data = request.json
        item_id = data.get('item_id')
        sess_id = session.get('cart_session_id')
        
        if sess_id:
            CartItem.query.filter_by(id=item_id, session_id=sess_id).delete()
            db.session.commit()
        
        count = 0
        if sess_id:
            from utils.database import CartItem as CI
            count = CI.query.filter_by(session_id=sess_id).count()
        return jsonify({'success': True, 'cart_count': count})

    @app.route('/api/cart/update', methods=['POST'])
    def api_cart_update():
        from utils.database import CartItem
        data = request.json
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        sess_id = session.get('cart_session_id')
        
        if sess_id and quantity > 0:
            item = CartItem.query.filter_by(id=item_id, session_id=sess_id).first()
            if item:
                item.quantity = quantity
                db.session.commit()
        elif sess_id and quantity <= 0:
            CartItem.query.filter_by(id=item_id, session_id=sess_id).delete()
            db.session.commit()
        return jsonify({'success': True})

    # Weather API Route
    @app.route('/api/weather')
    def api_weather():
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({'error': 'Location required'}), 400
        
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,surface_pressure&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            current = data['current']
            daily = data['daily']
            
            def map_wmo(code):
                if code == 0: return "Clear Sky", "01d"
                if code in [1, 2, 3]: return "Partly Cloudy", "02d"
                if code in [45, 48]: return "Fog", "50d"
                if code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]: return "Rain", "10d"
                if code >= 95: return "Thunderstorm", "11d"
                return "Unknown", "01d"
                
            condition, icon = map_wmo(current['weather_code'])
            temp = round(current['temperature_2m'])
            feels_like = round(current['apparent_temperature'])
            humidity = current['relative_humidity_2m']
            wind_speed = round(current['wind_speed_10m'])
            pressure = current['surface_pressure']
            rain_1h = current['precipitation']
            
            advice = []
            if humidity > 80:
                advice.append({"type": "warning", "icon": "🍄", "text": "High humidity alert! Risk of fungal diseases. Consider preventive fungicide spray."})
            if humidity < 40:
                advice.append({"type": "info", "icon": "💧", "text": "Low humidity. Increase irrigation frequency."})
            if temp > 38:
                advice.append({"type": "danger", "icon": "🌡️", "text": "Extreme heat! Irrigate crops early morning or evening."})
            if temp < 10:
                advice.append({"type": "info", "icon": "🥶", "text": "Cold conditions. Protect nursery seedlings."})
            if wind_speed > 30:
                advice.append({"type": "warning", "icon": "💨", "text": "High wind speed. Avoid spraying pesticides."})
            if rain_1h > 2:
                advice.append({"type": "info", "icon": "🌧️", "text": "Active rainfall detected. Hold off irrigation."})
            if current['weather_code'] >= 95:
                advice.append({"type": "danger", "icon": "⛈️", "text": "Thunderstorm active. Keep farm workers indoors."})
            if not advice:
                advice.append({"type": "success", "icon": "✅", "text": "Good farming conditions today. Ideal time for field operations."})
                
            forecast_list = []
            alert_generated = False
            
            for i in range(5):
                date = daily['time'][i]
                c_code = daily['weather_code'][i]
                c_cond, c_icon = map_wmo(c_code)
                rain_sum = daily['precipitation_sum'][i]
                max_t = daily['temperature_2m_max'][i]
                
                forecast_list.append({
                    'date': date,
                    'min_temp': round(daily['temperature_2m_min'][i]),
                    'max_temp': round(max_t),
                    'avg_humidity': humidity,
                    'rain_mm': rain_sum,
                    'condition': c_cond,
                    'icon': c_icon
                })
                
                if not alert_generated and 'user_id' in session:
                    from utils.database import Alert, db
                    user_id = session['user_id']
                    if rain_sum > 20 or max_t > 40 or c_code >= 95:
                        msg = f"Heavy rainfall ({rain_sum}mm) expected on {date}." if rain_sum > 20 else \
                              (f"Extreme heat ({max_t}°C) expected on {date}." if max_t > 40 else \
                              f"Severe thunderstorm expected on {date}.")
                        existing = Alert.query.filter_by(user_id=user_id, type="Weather Warning", message=msg).first()
                        if not existing:
                            new_alert = Alert(
                                user_id=user_id, type="Weather Warning", severity="warning",
                                message=msg, action_plan="/weather"
                            )
                            db.session.add(new_alert)
                            db.session.commit()
                            alert_generated = True

            return jsonify({
                'city': 'Your Location',
                'temp': temp,
                'feels_like': feels_like,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'condition': condition,
                'icon': icon,
                'pressure': pressure,
                'visibility': 10,
                'rain_1h': rain_1h,
                'advice': advice,
                'forecast': forecast_list
            })
        except Exception as e:
            print(f'Weather API error: {e}')
            return jsonify({'error': 'Failed to fetch weather data'}), 500

    return app

app = create_app()

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('notification', {'message': 'Connected to Real-Time Feed'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized.")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
