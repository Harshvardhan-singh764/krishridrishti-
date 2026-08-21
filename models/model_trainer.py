import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest

def train_crop_recommender():
    print("Training Crop Recommender...")
    # Generate dummy dataset for hackathon
    np.random.seed(42)
    n_samples = 1000
    
    # Features: N, P, K, temperature, humidity, ph, rainfall
    X = np.random.rand(n_samples, 7) * 100 
    X[:, 5] = X[:, 5] / 100 * 14  # pH scale 0-14
    
    crops = ['Rice', 'Maize', 'Jute', 'Cotton', 'Coconut', 'Papaya', 'Orange', 'Apple', 'Muskmelon', 'Watermelon', 'Grapes', 'Mango', 'Banana', 'Pomegranate', 'Lentil', 'Blackgram', 'Mungbean', 'Mothbeans', 'Pigeonpeas', 'Kidneybeans', 'Chickpea', 'Coffee']
    y = np.random.choice(crops, n_samples)
    
    # Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Train
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_scaled, y_encoded)
    
    # Save
    os.makedirs('models', exist_ok=True)
    joblib.dump(rf, 'models/crop_recommendation_model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')
    print("Crop Recommender saved.")

def train_anomaly_detector():
    print("Training Anomaly Detector...")
    # Generate normal sensor data with a few anomalies
    np.random.seed(42)
    # [Temperature, Moisture, pH, N, P, K]
    X_normal = np.random.normal(loc=[25, 40, 6.5, 50, 50, 50], scale=[2, 5, 0.5, 10, 10, 10], size=(900, 6))
    X_anomaly = np.random.uniform(low=[10, 10, 4.0, 10, 10, 10], high=[40, 80, 9.0, 100, 100, 100], size=(100, 6))
    X = np.vstack([X_normal, X_anomaly])
    
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(X)
    
    joblib.dump(clf, 'models/anomaly_detector.pkl')
    print("Anomaly Detector saved.")

def init_tf_models():
    print("Initializing TF models...")
    from disease_detector import CropDiseaseDetector
    from yield_predictor import YieldPredictor
    
    # Just build and save un-trained weights to have the files ready for the demo
    dd = CropDiseaseDetector(model_path='dummy') # force build
    dd.model.save('models/crop_disease_model.h5')
    
    yp = YieldPredictor(model_path='dummy') # force build
    yp.model.save('models/yield_prediction_model.h5')
    print("TF models saved.")

if __name__ == "__main__":
    train_crop_recommender()
    train_anomaly_detector()
    init_tf_models()
    print("All models initialized successfully!")
