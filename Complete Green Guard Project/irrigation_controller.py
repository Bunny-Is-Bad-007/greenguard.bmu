# created by Mushfiq
# created by Mushfiq
# created by Mushfiq
# created by Mushfiq
# created by Mushfiq
# created by Mushfiq
# created by Mushfiq
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import requests
import time
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage
import json
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='irrigation_system.log'
)

# Load credentials from environment variables or config file
load_dotenv()
THINGSPEAK_READ_API_KEY = os.getenv("THINGSPEAK_READ_API_KEY", "KK6M9X5V1DYT1F5F")
THINGSPEAK_WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY", "XTFR102X2F47ZAIX")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "fe1e2423f564b68143922b414bafac76")
EMAIL_USER = os.getenv("EMAIL_USER", "mushfiqul.alam.17@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Should be App Password
FARMER_PHONE = os.getenv("FARMER_PHONE", "6280357229")

# Configuration
THINGSPEAK_CHANNEL_ID = "2300946"
THINGSPEAK_READ_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_READ_API_KEY}&results=1"
THINGSPEAK_WRITE_URL = "https://api.thingspeak.com/update"

# Weather API configuration for Kapriwas, Haryana
LAT = 28.3167
LON = 76.9833
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"

# Crop-specific thresholds
CROP_PROFILES = {
    "wheat": {"ideal_moisture": 60, "max_temp": 35, "water_per_percent": 0.6, "max_water": 60},
    "rice": {"ideal_moisture": 80, "max_temp": 38, "water_per_percent": 0.8, "max_water": 80},
}

# Flask app initialization at module level
app = Flask(__name__)
CORS(app)

class ThingSpeakInterface:
    def __init__(self, read_url, write_url, write_api_key):
        self.read_url = read_url
        self.write_url = write_url
        self.write_api_key = write_api_key
        self.manual_control_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/5/last.json?api_key={THINGSPEAK_READ_API_KEY}"
        self.manual_value_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/6/last.json?api_key={THINGSPEAK_READ_API_KEY}"
    
    def read_sensor_data(self):
        """Read latest sensor data from ThingSpeak channel."""
        try:
            response = requests.get(self.read_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data or 'feeds' not in data or not data['feeds']:
                logging.warning("No data available from ThingSpeak")
                return None
                
            latest_feed = data['feeds'][-1]
            
            try:
                soil_moisture = float(latest_feed.get("field1", 0) or 0)
                temperature = float(latest_feed.get("field2", 0) or 0)
                humidity = float(latest_feed.get("field3", 0) or 0)
                raindrop_raw = float(latest_feed.get("field4", 0) or 0)
                
                raindrop = 100 * (1023 - raindrop_raw) / 1023 if not np.isnan(raindrop_raw) else 0.0
                
                sensor_data = {
                    "soil_moisture": soil_moisture if 0 <= soil_moisture <= 100 else 50.0,
                    "temperature": temperature if -10 <= temperature <= 50 else 25.0,
                    "humidity": humidity if 10 <= humidity <= 100 else 60.0,
                    "raindrop": raindrop if 0 <= raindrop <= 100 else 0.0
                }
                
                logging.info(f"Received data from ThingSpeak: {sensor_data}")
                return sensor_data
            except (ValueError, TypeError) as e:
                logging.error(f"Error parsing sensor values: {e}")
                return None
            
        except requests.RequestException as e:
            logging.error(f"Error reading from ThingSpeak: {e}")
            return None
    
    def check_manual_irrigation(self):
        """Check if manual irrigation is requested via ThingSpeak."""
        try:
            control_response = requests.get(self.manual_control_url, timeout=10)
            control_response.raise_for_status()
            
            control_data = control_response.json()
            manual_flag = int(float(control_data.get('field5', '0') or 0))
            
            if manual_flag == 1:
                value_response = requests.get(self.manual_value_url, timeout=10)
                value_response.raise_for_status()
                
                value_data = value_response.json()
                water_amount = float(value_data.get('field6', '0') or 0)
                return True, water_amount
                
            return False, 0
            
        except requests.RequestException as e:
            logging.error(f"Error checking manual irrigation: {e}")
            return False, 0
    
    def write_irrigation_command(self, water_amount, is_manual=False):
        """Write irrigation command to ThingSpeak channel."""
        try:
            payload = {
                'api_key': self.write_api_key,
                'field1': water_amount,
                'field2': 1 if is_manual else 0
            }
            response = requests.post(self.write_url, data=payload)
            if response.status_code == 200:
                mode = "Manual" if is_manual else "Automatic"
                logging.info(f"Sent {mode} irrigation command: {water_amount:.2f} liters")
                return True
            logging.error(f"ThingSpeak write error: Status code {response.status_code}")
            return False
        except Exception as e:
            logging.error(f"Error writing to ThingSpeak: {e}")
            return False

from model_manager import ModelManager

class IrrigationModel:
    def __init__(self):
        self.model_manager = ModelManager()
        self.model = self.load_or_train_model()
    
    def load_or_train_model(self):
        # Try to load existing model first
        model = self.model_manager.load_model()
        if model is not None:
            return model
            
        # If loading fails, train a new model
        logging.info("Training new irrigation model...")
        return self.train_new_model()
    
    def train_new_model(self):
        np.random.seed(42)
        num_samples = 1000
        data = {
            "soil_moisture": np.random.uniform(20, 80, num_samples),
            "temperature": np.random.uniform(20, 45, num_samples),
            "humidity": np.random.uniform(30, 90, num_samples),
            "rainfall_1d": np.random.uniform(0, 30, num_samples),
            "rainfall_3d": np.random.uniform(0, 80, num_samples),
            "raindrop": np.random.uniform(0, 100, num_samples),
        }
        data["water_needed"] = np.maximum(
            (70 - data["soil_moisture"]) * 0.6 +
            (data["temperature"] - 25) * 0.2 -
            (data["humidity"] - 50) * 0.1 -
            data["rainfall_1d"] * 0.3 -
            data["rainfall_3d"] * 0.1 -
            data["raindrop"] * 0.2,
            0
        )
        df = pd.DataFrame(data)
        X = df[["soil_moisture", "temperature", "humidity", "rainfall_1d", "rainfall_3d", "raindrop"]]
        y = df["water_needed"]
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        # Save the trained model using ModelManager
        self.model_manager.save_model(model)
        return model
    
    def predict(self, features):
        if self.model is None:
            raise Exception("Model not loaded")
        try:
            return max(0, self.model.predict(features)[0])
        except Exception as e:
            logging.error(f"Prediction error: {e}")
            return None

class WeatherService:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def get_forecast(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}")
            data = response.json()
            rainfall_1d = rainfall_3d = 0
            for i in range(min(8, len(data.get("list", [])))):
                rain_3h = data["list"][i].get("rain", {}).get("3h", 0)
                if i < 8:
                    rainfall_1d += rain_3h
                rainfall_3d += rain_3h
            return {"rainfall_1d": rainfall_1d, "rainfall_3d": rainfall_3d, "success": True}
        except Exception as e:
            logging.error(f"Weather API error: {e}")
            return {"rainfall_1d": 0, "rainfall_3d": 0, "success": False}

class NotificationService:
    def __init__(self, email, password, recipient):
        self.email = email
        self.password = password
        self.recipient = recipient
    
    def send_alert(self, message):
        logging.warning(f"Alert: {message}")
        try:
            msg = EmailMessage()
            msg.set_content(message)
            msg['Subject'] = 'GreenGuard Irrigation Alert'
            msg['From'] = self.email
            msg['To'] = self.recipient
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            logging.info("Email alert sent successfully")
            return True
        except Exception as e:
            logging.error(f"Email alert failed: {e}")
            return False

class IrrigationController:
    def __init__(self, crop_type="wheat"):
        if crop_type not in CROP_PROFILES:
            raise ValueError(f"Invalid crop type: {crop_type}")
        
        self.crop_type = crop_type
        self.model = IrrigationModel()
        self.thingspeak = ThingSpeakInterface(THINGSPEAK_READ_URL, THINGSPEAK_WRITE_URL, THINGSPEAK_WRITE_API_KEY)
        self.weather = WeatherService(WEATHER_URL)
        self.notifier = NotificationService(EMAIL_USER, EMAIL_PASSWORD, FARMER_PHONE)
        self.log_file = "irrigation_log.csv"
        self.last_manual_check = 0
        
        self._init_log_file()
    
    def _init_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("timestamp,soil_moisture,temperature,humidity,raindrop,rainfall_1d,rainfall_3d,water_amount,mode,crop_type,is_manual\n")
    
    def offline_prediction(self, soil_moisture, temperature, humidity, raindrop):
        profile = CROP_PROFILES[self.crop_type]
        water_needed = (profile["ideal_moisture"] - soil_moisture) * profile["water_per_percent"]
        
        if temperature > profile["max_temp"]:
            water_needed += 5
        water_needed -= (humidity - 50) * 0.1
        if raindrop > 50:
            water_needed -= 10
            
        return max(0, water_needed)
    
    def adjust_for_rainfall(self, water_needed, rainfall_1d, rainfall_3d):
        profile = CROP_PROFILES[self.crop_type]
        
        if rainfall_1d > 5:
            water_needed -= rainfall_1d * 0.5
        if rainfall_3d < 5:
            water_needed += 5
            
        return max(0, min(water_needed, profile["max_water"]))
    
    def check_manual_irrigation(self):
        current_time = time.time()
        if current_time - self.last_manual_check < 30:
            return False
            
        self.last_manual_check = current_time
        
        manual_mode, water_amount = self.thingspeak.check_manual_irrigation()
        if manual_mode and water_amount > 0:
            logging.info(f"Manual irrigation requested: {water_amount:.2f} liters")
            success = self.thingspeak.write_irrigation_command(water_amount, is_manual=True)
            
            if success:
                sensor_data = self.thingspeak.read_sensor_data() or {}
                log_data = {
                    "soil_moisture": sensor_data.get("soil_moisture", 0),
                    "temperature": sensor_data.get("temperature", 0),
                    "humidity": sensor_data.get("humidity", 0),
                    "raindrop": sensor_data.get("raindrop", 0),
                    "rainfall_1d": 0,
                    "rainfall_3d": 0,
                    "water_amount": water_amount,
                    "mode": "Manual",
                    "crop_type": self.crop_type,
                    "is_manual": 1
                }
                self.log_data(log_data)
                self.notifier.send_alert(f"Manual irrigation completed: {water_amount:.2f} liters")
            return True
        return False
    
    def log_data(self, data):
        try:
            with open(self.log_file, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp},{data['soil_moisture']:.2f},{data['temperature']:.2f},"
                       f"{data['humidity']:.2f},{data.get('raindrop', 0):.2f},"
                       f"{data.get('rainfall_1d', 0):.2f},{data.get('rainfall_3d', 0):.2f},"
                       f"{data['water_amount']:.2f},{data['mode']},{data['crop_type']},"
                       f"{data.get('is_manual', 0)}\n")
        except Exception as e:
            logging.error(f"Logging error: {e}")
            with open("error_log.txt", "a") as f:
                f.write(f"{datetime.now()}: Logging error - {str(e)}\n")
    
    def run(self):
        logging.info(f"GreenGuard Smart Irrigation System Running for {self.crop_type}")
        last_auto_check = 0
        auto_check_interval = 300
        while True:
            try:
                if self.check_manual_irrigation():
                    time.sleep(10)
                    continue
                
                current_time = time.time()
                if current_time - last_auto_check < auto_check_interval:
                    time.sleep(5)
                    continue
                
                last_auto_check = current_time
                
                sensor_data = self.thingspeak.read_sensor_data()
                if not sensor_data:
                    self.notifier.send_alert("Sensor data not received from ThingSpeak!")
                    time.sleep(60)
                    continue
                
                soil_moisture = sensor_data.get("soil_moisture", 0)
                temperature = sensor_data.get("temperature", 0)
                humidity = sensor_data.get("humidity", 0)
                raindrop = sensor_data.get("raindrop", 0)
                
                weather_data = self.weather.get_forecast()
                rainfall_1d = weather_data["rainfall_1d"]
                rainfall_3d = weather_data["rainfall_3d"]
                
                if weather_data["success"]:
                    input_features = pd.DataFrame([[
                        soil_moisture, temperature, humidity,
                        rainfall_1d, rainfall_3d, raindrop
                    ]], columns=["soil_moisture", "temperature", "humidity",
                               "rainfall_1d", "rainfall_3d", "raindrop"])
                    water_needed = self.model.predict(input_features)
                    prediction_mode = "ML-Model"
                else:
                    water_needed = self.offline_prediction(soil_moisture, temperature, humidity, raindrop)
                    prediction_mode = "Fallback"
                
                final_water = self.adjust_for_rainfall(water_needed, rainfall_1d, rainfall_3d)
                
                if final_water > 0:
                    logging.info(f"Irrigation needed: {final_water:.2f}L ({prediction_mode})")
                    self.thingspeak.write_irrigation_command(final_water, is_manual=False)
                else:
                    logging.info(f"No irrigation needed. Soil moisture: {soil_moisture:.1f}%")
                
                log_data = {
                    "soil_moisture": soil_moisture,
                    "temperature": temperature,
                    "humidity": humidity,
                    "raindrop": raindrop,
                    "rainfall_1d": rainfall_1d,
                    "rainfall_3d": rainfall_3d,
                    "water_amount": final_water,
                    "mode": prediction_mode,
                    "crop_type": self.crop_type,
                    "is_manual": 0
                }
                self.log_data(log_data)
            except KeyboardInterrupt:
                logging.info("Irrigation system stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in irrigation cycle: {e}")
                self.notifier.send_alert(f"System error: {str(e)}")
                time.sleep(60)

# Flask routes
@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    try:
        sensor_data = controller.thingspeak.read_sensor_data()
        if sensor_data:
            return jsonify(sensor_data)
        return jsonify({"error": "No sensor data available"}), 503
    except Exception as e:
        logging.error(f"Error in sensor-data endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_irrigation():
    try:
        data = request.get_json() or {}
        soil_moisture = float(data.get('soil_moisture', 50))
        temperature = float(data.get('temperature', 25))
        humidity = float(data.get('humidity', 60))
        raindrop = float(data.get('raindrop', 0))
        
        weather_data = controller.weather.get_forecast()
        input_features = pd.DataFrame([[soil_moisture, temperature, humidity, 
                                      weather_data["rainfall_1d"], weather_data["rainfall_3d"], raindrop]],
                                    columns=["soil_moisture", "temperature", "humidity", 
                                            "rainfall_1d", "rainfall_3d", "raindrop"])
        water_needed = controller.model.predict(input_features)
        final_water = controller.adjust_for_rainfall(water_needed, 
                                                   weather_data["rainfall_1d"], 
                                                   weather_data["rainfall_3d"])
        
        return jsonify({"predicted_water": final_water})
    except Exception as e:
        logging.error(f"Error in predict endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Global controller instance
controller = IrrigationController(crop_type="wheat")

if __name__ == "__main__":
    # Start controller in a separate thread
    controller_thread = threading.Thread(target=controller.run, daemon=True)
    controller_thread.start()
    
    # Run Flask app
    logging.info("Starting Flask API on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
