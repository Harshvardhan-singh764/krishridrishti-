from sklearn.ensemble import IsolationForest
import joblib
import os
import numpy as np

class AnomalyDetector:
    def __init__(self, model_path='models/anomaly_detector.pkl'):
        self.model_path = model_path
        self.model = None
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = IsolationForest(contamination=0.1, random_state=42)
            # Not fitted yet
    
    def detect_anomalies(self, data):
        # data: array of sensor readings or weather data
        try:
            if not hasattr(self.model, "estimators_"):
                # Mock if not trained
                # Randomly flag 5% as anomalies
                return np.random.choice([1, -1], size=len(data), p=[0.95, 0.05])
                
            anomalies = self.model.predict(data)
            return anomalies
        except Exception:
            return np.ones(len(data))
