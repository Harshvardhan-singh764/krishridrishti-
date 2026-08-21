# 🌱 AgriDrishti AI - Hackathon Project

A fully functional, real-time AI-powered agriculture intelligence platform.

## Features Included
1. **AI Crop Scanner:** Powered by TensorFlow MobileNetV2 for leaf disease detection.
2. **Crop Recommendation:** Random Forest model for personalized crop suggestions based on soil data.
3. **Yield Prediction:** LSTM Deep Learning model for yield forecasting.
4. **Real-time WebSockets:** Live streaming of simulated soil, weather, and anomaly alerts.
5. **Beautiful UI/UX:** "White & Persian Green" theme with glassmorphism effects and responsive layouts.

## Setup Instructions

### 1. Standard Python Setup (Local)
1. Navigate to the project directory:
   ```bash
   cd "C:\Users\pooja\OneDrive\Desktop\SIH AGRIDRISHTI\agritech_ai_platform"
   ```
2. Install dependencies (we recommend using a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the AI models (This will generate dummy models for the demo so it runs fast!):
   ```bash
   python models/model_trainer.py
   ```
4. Start the Application:
   ```bash
   python app.py
   ```
5. Open your browser and go to `http://127.0.0.0:5000`. Login with username `demo` and password `password123`.

### 2. Docker Setup
To run everything in an isolated container:
```bash
docker-compose up -d --build
```

Enjoy the hackathon! 🚀
