from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os
import numpy as np

class YieldPredictor:
    def __init__(self, model_path='models/yield_prediction_model.h5'):
        self.model_path = model_path
        if os.path.exists(model_path):
            import tensorflow as tf
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = self.build_model()
            
    def build_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(12, 4)),
            Dropout(0.2),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def predict(self, historical_data, weather_forecast):
        # Dummy mock logic for hackathon
        # historical_data and weather_forecast would normally be processed to shape (1, 12, 4)
        mock_input = np.random.rand(1, 12, 4)
        prediction = self.model.predict(mock_input)
        return float(prediction[0][0]) * 100 # arbitrary scale for demo
