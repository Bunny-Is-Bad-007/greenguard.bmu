# created by Mushfiq
# created by Mushfiq

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os

# Create Flask app and enable CORS
app = Flask(__name__)
CORS(app)  # This allows all origins

# Load the trained model
# Adjust path if needed
MODEL_PATH = 'water_model.pkl'

# Check if model exists, otherwise provide instructions
if not os.path.exists(MODEL_PATH):
    print(f"Model file '{MODEL_PATH}' not found! Please run train_model.py first.")
    print("You can use the mock responses for testing until the model is available.")

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Using mock responses for now.")
    model = None

# Sample irrigation history data (replace with database in production)
irrigation_history = [
    {"date": "2025-02-25", "actual_water": 45, "predicted_water": 42},
    {"date": "2025-02-24", "actual_water": 50, "predicted_water": 48},
    {"date": "2025-02-23", "actual_water": 38, "predicted_water": 35},
    {"date": "2025-02-22", "actual_water": 42, "predicted_water": 40},
    {"date": "2025-02-21", "actual_water": 55, "predicted_water": 52},
]

@app.route('/predict', methods=['POST'])
def predict():
    """Predict irrigation needs based on sensor data"""
    try:
        # Get data from request
        data = request.json
        soil_moisture = data.get('soil_moisture', 30)
        temperature = data.get('temperature', 28)
        
        # Log the incoming data
        print(f"Received prediction request: soil_moisture={soil_moisture}, temperature={temperature}")
        
        # Check if we have a model
        if model is not None:
            # Prepare data for model
            input_data = [[soil_moisture, temperature]]
            
            # Make prediction using the model
            predicted_water = float(model.predict(input_data)[0])
            
            # Calculate rainfall forecast (mock for now, replace with actual API call)
            rainfall_forecast = 32.61  # Example value
            
            # Create decision message
            if rainfall_forecast > 20:
                decision = f"💧 Less Water Needed: {predicted_water:.2f} liters (Rain forecasted)"
            else:
                decision = f"💧 Recommended Water: {predicted_water:.2f} liters"
        else:
            # Mock response if model is not available
            predicted_water = 10.05
            rainfall_forecast = 32.61
            decision = "💧 Less Water Needed: 10.05 liters (Rain forecasted)"
        
        # Return prediction
        return jsonify({
            'predicted_water': predicted_water,
            'rainfall_forecast': rainfall_forecast,
            'decision': decision
        })
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({
            'error': str(e),
            'predicted_water': 10.05,  # Default fallback
            'rainfall_forecast': 0.0,
            'decision': f"Error: {str(e)}"
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Return irrigation history"""
    try:
        return jsonify({
            'history': irrigation_history
        })
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/start-irrigation', methods=['POST'])
def start_irrigation():
    """Start irrigation with given amount"""
    try:
        data = request.json
        water_amount = data.get('water_amount', 0)
        
        # Log the request
        print(f"Starting irrigation with {water_amount} liters")
        
        # In a real implementation, this would control a pump
        # For now, just log it and save to history
        new_record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "actual_water": water_amount,
            "predicted_water": data.get('predicted_water', water_amount)
        }
        
        # Add to history (in a real app, save to database)
        irrigation_history.insert(0, new_record)
        
        return jsonify({
            'status': 'success',
            'message': f'Started irrigation with {water_amount} liters'
        })
    except Exception as e:
        print(f"Error starting irrigation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop-irrigation', methods=['POST'])
def stop_irrigation():
    """Stop irrigation and calculate dispensed amount"""
    try:
        data = request.json
        dispensed_amount = data.get('dispensed_amount', 0)
        
        # Log the request
        print(f"Stopping irrigation, dispensed {dispensed_amount} liters")
        
        # In a real implementation, this would stop a pump
        return jsonify({
            'status': 'success',
            'message': f'Stopped irrigation after dispensing {dispensed_amount} liters'
        })
    except Exception as e:
        print(f"Error stopping irrigation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    """Return current sensor data (mock for now)"""
    try:
        # In a real implementation, this would read from sensors
        # For now, return mock data
        return jsonify({
            'soil_moisture': 30,  # Percentage
            'temperature': 28,    # Celsius
        })
    except Exception as e:
        print(f"Error getting sensor data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on port 8000
    port = 8000
    print(f"Starting Flask server on http://127.0.0.1:{port}")
    print("API Endpoints:")
    print(f"  - GET  http://127.0.0.1:{port}/history")
    print(f"  - GET  http://127.0.0.1:{port}/sensor-data")
    print(f"  - POST http://127.0.0.1:{port}/predict")
    print(f"  - POST http://127.0.0.1:{port}/start-irrigation")
    print(f"  - POST http://127.0.0.1:{port}/stop-irrigation")
    app.run(host='0.0.0.0', port=port, debug=True)
