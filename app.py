
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
                email='demo@agridrishti.com',
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
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
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
        return render_template('alerts.html')

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
            {'state': 'MP', 'market': 'Indore', 'commodity': 'Soyabean', 'variety': 'Yellow', 'date': today, 'min_price': '4200', 'max_price': '4600', 'modal_price': '4450'}
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
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
            prompt = (
                f"Based on these soil and weather parameters for farming in India:\n"
                f"Nitrogen (N): {data.get('N')} kg/ha\n"
                f"Phosphorus (P): {data.get('P')} kg/ha\n"
                f"Potassium (K): {data.get('K')} kg/ha\n"
                f"pH: {data.get('ph')}\n"
                f"Temperature: {data.get('temperature')} °C\n"
                f"Humidity: {data.get('humidity')} %\n"
                f"Rainfall: {data.get('rainfall')} mm\n"
                f"Recommend the top 3 best crops. Return exactly the following JSON structure: "
                f"{{\"crops\": [\"Crop1\", \"Crop2\", \"Crop3\"], \"probabilities\": [0.85, 0.12, 0.03]}}"
            )
            payload = {
                'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0.5, 'responseMimeType': 'application/json'}
            }
            resp = requests.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            resp_data = resp.json()
            text = resp_data['candidates'][0]['content']['parts'][0]['text']
            result = json.loads(text)
            return jsonify(result)
        except Exception as e:
            print(f'Gemini recommend error: {e}')
            return jsonify({'crops': ["Wheat", "Mustard", "Gram"], 'probabilities': [0.85, 0.12, 0.03]})

    @app.route('/api/scan', methods=['POST'])
    def api_scan():
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        file = request.files['image']
        
        gemini_key = app.config.get('GEMINI_API_KEY')
        if not gemini_key:
            return jsonify({'error': 'Gemini API key is missing'}), 500
            
        try:
            import base64
            import json
            encoded_image = base64.b64encode(file.read()).decode('utf-8')
            mime_type = file.content_type
            
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
            prompt = (
                "Analyze this plant leaf image. Identify the crop and any disease present. "
                "Provide the disease name, confidence level (e.g. 95%), and 3 recommended treatment steps. "
                "Output exactly as JSON: {\"disease\": \"...\", \"confidence\": \"...\", \"treatment\": [\"...\", \"...\", \"...\"]}"
            )
            payload = {
                'contents': [{
                    'role': 'user',
                    'parts': [
                        {'text': prompt},
                        {'inline_data': {'mime_type': mime_type, 'data': encoded_image}}
                    ]
                }],
                'generationConfig': {'temperature': 0.2, 'responseMimeType': 'application/json'}
            }
            resp = requests.post(url, json=payload, timeout=20)
            resp.raise_for_status()
            resp_data = resp.json()
            text = resp_data['candidates'][0]['content']['parts'][0]['text']
            
            result = json.loads(text)
            return jsonify(result)
        except Exception as e:
            print(f'Gemini scan error: {e}')
            return jsonify({'error': 'Failed to analyze image'}), 500

    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        data = request.json
        msg = data.get('message', '')
        
        gemini_key = app.config.get('GEMINI_API_KEY')
        
        if gemini_key:
            try:
                import json
                url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
                system_prompt = (
                    'You are AgriDrishti AI, an expert agricultural assistant for Indian farmers. '
                    'You have deep knowledge of crops, soil health, pest management, fertilizers, seeds, '
                    'weather patterns affecting farming, crop diseases, irrigation techniques, and government '
                    'agricultural schemes. Always give practical, actionable advice in simple language. '
                    'If asked about specific pesticides or seeds, provide dosage, usage, and safety info. '
                    'Respond in the same language the user uses (Hindi, English, or regional languages).'
                )
                payload = {
                    'contents': [
                        {
                            'role': 'user',
                            'parts': [{'text': system_prompt + '\n\nUser question: ' + msg}]
                        }
                    ],
                    'generationConfig': {
                        'temperature': 0.7,
                        'maxOutputTokens': 1024
                    }
                }
                resp = requests.post(url, json=payload, timeout=15)
                resp_data = resp.json()
                reply = resp_data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'reply': reply, 'powered_by': 'gemini'})
            except Exception as e:
                print(f'Gemini API error: {e}')
                return jsonify({'reply': 'Sorry, I am having trouble connecting to my AI brain right now.', 'powered_by': 'error'}), 500
        else:
            return jsonify({'reply': 'My Gemini API key is missing. Please configure it.', 'powered_by': 'error'}), 500

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
        weather_key = app.config.get('OPENWEATHER_API_KEY')
        
        if not lat or not lon:
            return jsonify({'error': 'Location required'}), 400
        
        try:
            # Current weather
            current_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_key}&units=metric'
            forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_key}&units=metric&cnt=40'
            
            current_resp = requests.get(current_url, timeout=10)
            forecast_resp = requests.get(forecast_url, timeout=10)
            
            current = current_resp.json()
            forecast = forecast_resp.json()
            
            # Check for API-level errors (invalid key, rate limit, etc.)
            if str(current.get('cod', 200)) not in ('200', '200.0'):
                raise Exception(f"OpenWeatherMap error: {current.get('message', 'Unknown')} (cod {current.get('cod')})")
            
            # Extract current conditions
            temp = round(current['main']['temp'])
            feels_like = round(current['main']['feels_like'])
            humidity = current['main']['humidity']
            wind_speed = round(current['wind']['speed'] * 3.6)  # m/s to km/h
            condition = current['weather'][0]['description'].title()
            condition_code = current['weather'][0]['id']
            icon = current['weather'][0]['icon']
            pressure = current['main']['pressure']
            visibility = current.get('visibility', 0) // 1000
            city = current.get('name', 'Your Location')
            rain_1h = current.get('rain', {}).get('1h', 0)
            
            # Agriculture advice
            advice = []
            if humidity > 80:
                advice.append({"type": "warning", "icon": "🍄", "text": "High humidity alert! Risk of fungal diseases. Consider preventive fungicide spray (Mancozeb/Ridomil Gold)."})
            if humidity < 40:
                advice.append({"type": "info", "icon": "💧", "text": "Low humidity. Increase irrigation frequency. Check soil moisture every 24 hours."})
            if temp > 38:
                advice.append({"type": "danger", "icon": "🌡️", "text": "Extreme heat! Irrigate crops early morning or evening. Avoid pesticide application."})
            if temp < 10:
                advice.append({"type": "info", "icon": "🥶", "text": "Cold conditions. Protect nursery seedlings. Frost risk — cover sensitive plants overnight."})
            if wind_speed > 30:
                advice.append({"type": "warning", "icon": "💨", "text": "High wind speed. Avoid spraying pesticides or fertilizers. Risk of lodging in tall crops."})
            if rain_1h > 5:
                advice.append({"type": "info", "icon": "🌧️", "text": "Active rainfall detected. Hold off irrigation and pesticide/fertilizer application."})
            if condition_code >= 200 and condition_code < 300:
                advice.append({"type": "danger", "icon": "⛈️", "text": "Thunderstorm active. Keep farm workers indoors. Secure equipment and protect produce."})
            if not advice:
                advice.append({"type": "success", "icon": "✅", "text": "Good farming conditions today. Ideal time for field operations, spraying, and irrigation."})
            
            # Process 5-day forecast
            daily_forecast = {}
            for item in forecast.get('list', []):
                date = item['dt_txt'].split(' ')[0]
                if date not in daily_forecast:
                    daily_forecast[date] = {
                        'date': date,
                        'temps': [],
                        'humidity': [],
                        'rain': 0,
                        'condition': item['weather'][0]['description'].title(),
                        'icon': item['weather'][0]['icon']
                    }
                daily_forecast[date]['temps'].append(item['main']['temp'])
                daily_forecast[date]['humidity'].append(item['main']['humidity'])
                if 'rain' in item:
                    daily_forecast[date]['rain'] += item.get('rain', {}).get('3h', 0)
            
            forecast_list = []
            for date, d in list(daily_forecast.items())[:7]:
                forecast_list.append({
                    'date': date,
                    'min_temp': round(min(d['temps'])),
                    'max_temp': round(max(d['temps'])),
                    'avg_humidity': round(sum(d['humidity']) / len(d['humidity'])),
                    'rain_mm': round(d['rain'], 1),
                    'condition': d['condition'],
                    'icon': d['icon']
                })
            
            return jsonify({
                'city': city,
                'temp': temp,
                'feels_like': feels_like,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'condition': condition,
                'icon': icon,
                'pressure': pressure,
                'visibility': visibility,
                'rain_1h': rain_1h,
                'advice': advice,
                'forecast': forecast_list
            })
        except Exception as e:
            print(f'Weather API error: {e}')
            # Return smart seasonal mock data so UI still works
            import datetime, random, math
            month = datetime.datetime.now().month
            base_temp = 28 + 8 * math.sin((month - 4) * math.pi / 6)
            temp = round(base_temp + random.uniform(-2, 2))
            humidity = random.randint(60, 80) if month in [6,7,8,9] else random.randint(35, 55)
            wind_speed = random.randint(8, 18)
            condition = 'Partly Cloudy' if month in [6,7,8,9] else 'Clear Sky'
            advice = [{"type": "success", "icon": "\u2705", "text": "Good farming conditions today. Ideal time for field operations and irrigation."}]
            if humidity > 65:
                advice.append({"type": "warning", "icon": "\U0001f344", "text": "Moderate humidity. Monitor crops for early signs of fungal disease."})
            today = datetime.date.today()
            forecast_list = []
            for i in range(7):
                fdate = today + datetime.timedelta(days=i)
                forecast_list.append({
                    'date': fdate.isoformat(),
                    'min_temp': temp - random.randint(3, 5),
                    'max_temp': temp + random.randint(2, 4),
                    'avg_humidity': humidity + random.randint(-5, 5),
                    'rain_mm': round(random.uniform(0, 3) if month in [6,7,8,9] else 0, 1),
                    'condition': condition, 'icon': '02d'
                })
            return jsonify({
                'city': 'Your Location (offline mode)',
                'temp': temp, 'feels_like': temp - 2, 'humidity': humidity,
                'wind_speed': wind_speed, 'condition': condition, 'icon': '02d',
                'pressure': 1013, 'visibility': 10, 'rain_1h': 0,
                'advice': advice, 'forecast': forecast_list, 'is_mock': True
            })

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
