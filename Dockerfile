FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for OpenCV and ML libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize dummy models and DB during build
RUN python models/model_trainer.py
RUN python -c "from app import init_db; init_db()"

EXPOSE 5000

CMD ["python", "app.py"]
