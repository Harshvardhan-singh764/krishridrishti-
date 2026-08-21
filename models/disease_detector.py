import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import numpy as np
import cv2
import os

class CropDiseaseDetector:
    def __init__(self, model_path='models/crop_disease_model.h5'):
        self.classes = ['Healthy', 'Bacterial Spot', 'Early Blight', 
                       'Late Blight', 'Leaf Mold', 'Septoria Leaf Spot']
        self.model_path = model_path
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = self.build_model()
            
    def build_model(self):
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        predictions = Dense(len(self.classes), activation='softmax')(x)
        model = Model(inputs=base_model.input, outputs=predictions)
        model.compile(optimizer='adam', loss='categorical_crossentropy', 
                     metrics=['accuracy'])
        return model
    
    def predict(self, image_path):
        if not os.path.exists(image_path):
            return None, 0.0
            
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)
        
        preds = self.model.predict(img)
        class_idx = np.argmax(preds[0])
        confidence = float(preds[0][class_idx]) * 100
        
        return self.classes[class_idx], confidence
