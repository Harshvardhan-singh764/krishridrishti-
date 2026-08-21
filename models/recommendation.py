from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import numpy as np

class CropRecommender:
    def __init__(self, model_path='models/crop_recommendation_model.pkl', 
                 scaler_path='models/scaler.pkl', 
                 label_encoder_path='models/label_encoder.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.label_encoder_path = label_encoder_path
        
        self.model = None
        self.scaler = None
        self.label_encoder = None
        
        if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(label_encoder_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(label_encoder_path)
    
    def recommend(self, soil_data):
        # soil_data: [N, P, K, temperature, humidity, ph, rainfall]
        if self.model is None or self.scaler is None:
            # Fallback for hackathon demo if model isn't trained
            return ["Rice", "Wheat", "Maize"], [0.85, 0.10, 0.05]
            
        features = self.scaler.transform([soil_data])
        prediction_idx = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_crops = self.label_encoder.inverse_transform(top_indices)
        top_probs = probabilities[top_indices]
        
        return list(top_crops), list(top_probs)
