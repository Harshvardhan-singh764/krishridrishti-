from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='farmer')
    farm_size = db.Column(db.Float)
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    farms = db.relationship('Farm', backref='user', lazy=True)
    scans = db.relationship('CropScan', backref='user', lazy=True)
    alerts = db.relationship('Alert', backref='user', lazy=True)

class Farm(db.Model):
    __tablename__ = 'farms'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    farm_name = db.Column(db.String(100))
    total_area = db.Column(db.Float)
    location = db.Column(db.String(255))
    soil_type = db.Column(db.String(50))
    crops_planted = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    soil_health = db.relationship('SoilHealth', backref='farm', lazy=True)
    yield_predictions = db.relationship('YieldPrediction', backref='farm', lazy=True)

class CropScan(db.Model):
    __tablename__ = 'crop_scans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_path = db.Column(db.String(255))
    crop_type = db.Column(db.String(50))
    health_status = db.Column(db.String(20))
    disease = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    recommendations = db.Column(db.Text)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    forecast = db.Column(db.Text) # JSON string
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class SoilHealth(db.Model):
    __tablename__ = 'soil_health'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
    ph_level = db.Column(db.Float)
    nitrogen = db.Column(db.Integer)
    phosphorus = db.Column(db.Integer)
    potassium = db.Column(db.Integer)
    moisture = db.Column(db.Float)
    temperature = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    message = db.Column(db.Text)
    action_plan = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class YieldPrediction(db.Model):
    __tablename__ = 'yield_predictions'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
    crop_type = db.Column(db.String(50))
    predicted_yield = db.Column(db.Float)
    confidence_interval = db.Column(db.Text) # JSON string
    season = db.Column(db.String(20))
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(100))
    message = db.Column(db.Text)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100))
    category = db.Column(db.String(50))  # 'seed', 'pesticide', 'medicine', 'fertilizer', 'tool'
    sub_category = db.Column(db.String(100))  # e.g. 'vegetable_seed', 'herbicide', 'fungicide'
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # for discount display
    stock = db.Column(db.Integer, default=100)
    unit = db.Column(db.String(50))  # e.g. '1 kg', '500 ml', '250 g'
    description = db.Column(db.Text)
    usage_instructions = db.Column(db.Text)
    safety_info = db.Column(db.Text)
    active_ingredient = db.Column(db.String(200))
    crop_suitable_for = db.Column(db.String(300))
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=4.2)
    reviews_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='cart_items')
