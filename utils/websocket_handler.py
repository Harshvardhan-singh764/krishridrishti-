import random
import time
from threading import Thread

class BackgroundTasks:
    def __init__(self, socketio, app):
        self.socketio = socketio
        self.app = app
        self.running = False
        
    def start(self):
        if not self.running:
            self.running = True
            Thread(target=self.emit_weather_updates, daemon=True).start()
            Thread(target=self.emit_sensor_updates, daemon=True).start()
            Thread(target=self.emit_alerts, daemon=True).start()
            
    def emit_weather_updates(self):
        with self.app.app_context():
            while self.running:
                # Simulate weather changes
                data = {
                    'temperature': round(random.uniform(22.0, 35.0), 1),
                    'humidity': round(random.uniform(40.0, 85.0), 1),
                    'wind_speed': round(random.uniform(2.0, 15.0), 1),
                    'condition': random.choice(['Clear', 'Partly Cloudy', 'Rain', 'Thunderstorm'])
                }
                self.socketio.emit('weather_update', data)
                time.sleep(10) # update every 10 seconds for demo purposes
                
    def emit_sensor_updates(self):
        with self.app.app_context():
            while self.running:
                # Simulate soil sensor changes
                data = {
                    'moisture': round(random.uniform(30.0, 60.0), 1),
                    'nitrogen': random.randint(40, 80),
                    'phosphorus': random.randint(30, 60),
                    'potassium': random.randint(30, 60),
                    'ph': round(random.uniform(5.5, 7.5), 2)
                }
                self.socketio.emit('sensor_update', data)
                time.sleep(5) # fast updates for demo
                
    def emit_alerts(self):
        with self.app.app_context():
            while self.running:
                time.sleep(30) # occasional alerts
                alerts = [
                    {'type': 'warning', 'message': 'High temperature expected this afternoon. Consider irrigating.'},
                    {'type': 'danger', 'message': 'Pest anomaly detected in Sector A. Action required.'},
                    {'type': 'info', 'message': 'Soil moisture optimal. Irrigation paused.'}
                ]
                self.socketio.emit('new_alert', random.choice(alerts))
