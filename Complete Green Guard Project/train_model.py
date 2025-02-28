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

# Your ThingSpeak credentials and configuration
# ThingSpeak channels
THINGSPEAK_READ_API_KEY = "KK6M9X5V1DYT1F5F"  # ESP32 to AI (sensor data)
THINGSPEAK_CHANNEL_ID = "2300946"
THINGSPEAK_READ_URL = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_READ_API_KEY}&results=1"

THINGSPEAK_WRITE_API_KEY = "XTFR102X2F47ZAIX"  # AI to ESP32 (irrigation commands)
THINGSPEAK_WRITE_URL = "https://api.thingspeak.com/update"

# Weather API configuration for Jalandhar, India
WEATHER_API_KEY = "fe1e2423f564b68143922b414bafac76"
LAT = 31.3260  # Jalandhar latitude
LON = 75.5762  # Jalandhar longitude
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"

# Email/SMS configuration
EMAIL_USER = "mushfiqul.alam.17@gmail.com"
EMAIL_PASSWORD = "Mushfiq@BMU"  # Consider using app password for Gmail
FARMER_PHONE = "6280357229"

# Crop-specific thresholds
CROP_PROFILES = {
    "wheat": {"ideal_moisture": 60, "max_temp": 35, "water_per_percent": 0.6, "max_water": 60},
    "rice": {"ideal_moisture": 80, "max_temp": 38, "water_per_percent": 0.8, "max_water": 80},
}

# ThingSpeak data interface
class ThingSpeakInterface:
    def __init__(self, read_url, write_url, write_api_key):
        self.read_url = read_url
        self.write_url = write_url
        self.write_api_key = write_api_key
        self.manual_control_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/5/last.json?api_key={THINGSPEAK_READ_API_KEY}"
        self.manual_value_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/6/last.json?api_key={THINGSPEAK_READ_API_KEY}"
    
    def read_sensor_data(self):
        """Read latest sensor data from ThingSpeak channel"""
        try:
            response = requests.get(self.read_url, timeout=10)
            if response.status_code != 200:
                print(f"ThingSpeak read error: Status code {response.status_code}")
                return None
            
            data = response.json()
            if not data or 'feeds' not in data or not data['feeds']:
                print("No data available from ThingSpeak")
                return None
                
            # Extract the latest feed
            latest_feed = data['feeds'][-1]
            
            # Parse sensor values with better error handling
            try:
                soil_moisture = float(latest_feed.get("field1", 0))
                temperature = float(latest_feed.get("field2", 0))
                humidity = float(latest_feed.get("field3", 0))
                raindrop_raw = float(latest_feed.get("field4", 0))
                
                # Normalize raindrop value (0-1023 to 0-100%, where 100% = heavy rain)
                raindrop = 100 * (1023 - raindrop_raw) / 1023 if not np.isnan(raindrop_raw) else 0.0
                
                # Check for NaN values and unrealistic values, replace with defaults
                sensor_data = {
                    "soil_moisture": soil_moisture if not np.isnan(soil_moisture) and 0 <= soil_moisture <= 100 else 50.0,
                    "temperature": temperature if not np.isnan(temperature) and -10 <= temperature <= 50 else 25.0,
                    "humidity": humidity if not np.isnan(humidity) and 10 <= humidity <= 100 else 60.0,  # Minimum 10% humidity
                    "raindrop": raindrop if not np.isnan(raindrop) and 0 <= raindrop <= 100 else 0.0
                }
                
                print(f"Received data from ThingSpeak: {sensor_data}")
                return sensor_data
            except (ValueError, TypeError) as e:
                print(f"Error parsing sensor values: {e}")
                return None
            
        except Exception as e:
            print(f"Error reading from ThingSpeak: {e}")
            return None
    
    def check_manual_irrigation(self):
        """Check if manual irrigation is requested via ThingSpeak"""
        try:
            # Get manual control flag (field5)
            control_response = requests.get(self.manual_control_url, timeout=10)
            if control_response.status_code != 200:
                return False, 0
            
            control_data = control_response.json()
            manual_flag = int(float(control_data.get('field5', '0')))
            
            # If manual mode is enabled, get the water amount (field6)
            if manual_flag == 1:
                value_response = requests.get(self.manual_value_url, timeout=10)
                if value_response.status_code != 200:
                    return False, 0
                
                value_data = value_response.json()
                water_amount = float(value_data.get('field6', '0'))
                return True, water_amount
                
            return False, 0
            
        except Exception as e:
            print(f"Error checking manual irrigation: {e}")
            return False, 0
    
    def write_irrigation_command(self, water_amount, is_manual=False):
        """Write irrigation command to ThingSpeak channel"""
        try:
            # Prepare data package
            payload = {
                'api_key': self.write_api_key,
                'field1': water_amount,  # Send water amount to field1 of output channel
                'field2': 1 if is_manual else 0  # Flag to indicate if this is manual or automatic irrigation
            }
            
            # Send to ThingSpeak
            response = requests.post(self.write_url, data=payload)
            if response.status_code == 200:
                mode = "Manual" if is_manual else "Automatic"
                print(f"📡 Sent {mode} irrigation command: {water_amount:.2f} liters")
                return True
            else:
                print(f"ThingSpeak write error: Status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error writing to ThingSpeak: {e}")
            return False

# Model training and management
class IrrigationModel:
    def __init__(self, model_path="water_model.pkl"):
        self.model_path = model_path
        self.model = self.load_or_train_model()
    
    def load_or_train_model(self):
        """Load existing model or train a new one if not available"""
        if os.path.exists(self.model_path):
            print(f"Loading existing model from {self.model_path}")
            return joblib.load(self.model_path)
        else:
            print("Training new irrigation model...")
            return self.train_new_model()
    
    def train_new_model(self):
        """Train a new RandomForest model for irrigation prediction"""
        np.random.seed(42)
        num_samples = 1000  # Increased sample size
        
        # Generate synthetic training data
        data = {
            "soil_moisture": np.random.uniform(20, 80, num_samples),
            "temperature": np.random.uniform(20, 45, num_samples),
            "humidity": np.random.uniform(30, 90, num_samples),
            "rainfall_1d": np.random.uniform(0, 30, num_samples),
            "rainfall_3d": np.random.uniform(0, 80, num_samples),
            "raindrop": np.random.uniform(0, 100, num_samples),  # Added raindrop sensor
        }
        
        # Create target variable with weighted influence from all features
        data["water_needed"] = (70 - data["soil_moisture"]) * 0.6 + \
                              (data["temperature"] - 25) * 0.2 - \
                              (data["humidity"] - 50) * 0.1 - \
                              data["rainfall_1d"] * 0.3 - \
                              data["rainfall_3d"] * 0.1 - \
                              data["raindrop"] * 0.2
        
        # Ensure water needed is never negative
        data["water_needed"] = np.maximum(data["water_needed"], 0)
        
        # Create and train model
        df = pd.DataFrame(data)
        X = df[["soil_moisture", "temperature", "humidity", "rainfall_1d", "rainfall_3d", "raindrop"]]
        y = df["water_needed"]
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Print feature importance
        feature_importance = dict(zip(X.columns, model.feature_importances_))
        print("Feature importance:")
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            print(f"- {feature}: {importance:.4f}")
        
        # Save model to file
        joblib.dump(model, self.model_path)
        print(f"Model trained and saved to {self.model_path}")
        return model
    
    def predict(self, features):
        """Make prediction using trained model"""
        if self.model is None:
            raise Exception("Model not loaded")
        
        try:
            prediction = self.model.predict(features)[0]
            return max(0, prediction)  # Ensure non-negative
        except Exception as e:
            print(f"Prediction error: {e}")
            return None

# Weather service
class WeatherService:
    def __init__(self, api_url):
        self.api_url = api_url
    
    def get_forecast(self):
        """Fetch weather forecast from OpenWeather API"""
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}")
            
            data = response.json()
            
            # Extract rainfall predictions for next day and 3 days
            rainfall_1d = 0
            rainfall_3d = 0
            
            # Check if we have precipitation data
            for i in range(min(8, len(data.get("list", [])))):
                # Get 3h rain value or default to 0
                rain_3h = data["list"][i].get("rain", {}).get("3h", 0)
                
                # First day rainfall (8 3-hour periods)
                if i < 8:
                    rainfall_1d += rain_3h
                
                # 3-day rainfall
                rainfall_3d += rain_3h
            
            return {
                "rainfall_1d": rainfall_1d,
                "rainfall_3d": rainfall_3d,
                "success": True
            }
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return {
                "rainfall_1d": 0,
                "rainfall_3d": 0,
                "success": False
            }

# Notification service
class NotificationService:
    def __init__(self, email, password, recipient):
        self.email = email
        self.password = password
        self.recipient = recipient
    
    def send_alert(self, message):
        """Send alert via email/SMS"""
        try:
            print(f"⚠️ Alert: {message}")  # Always print the alert
            
            try:
                # Create email message
                msg = EmailMessage()
                msg.set_content(message)
                msg['Subject'] = 'GreenGuard Irrigation Alert'
                msg['From'] = self.email
                msg['To'] = self.recipient
                
                # Connect to Gmail and send
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(self.email, self.password)
                    server.send_message(msg)
                
                print(f"📩 Email alert sent successfully")
                return True
            except Exception as e:
                print(f"📧 Email alert failed (continuing anyway): {str(e)}")
                return False  # Continue execution even if email fails
        except Exception as e:
            print(f"⚠️ Alert failed: {e}")
            return False

# Main Irrigation Controller
class IrrigationController:
    def __init__(self, crop_type="wheat"):
        self.crop_type = crop_type
        self.model = IrrigationModel()
        self.thingspeak = ThingSpeakInterface(THINGSPEAK_READ_URL, THINGSPEAK_WRITE_URL, THINGSPEAK_WRITE_API_KEY)
        self.weather = WeatherService(WEATHER_URL)
        self.notifier = NotificationService(EMAIL_USER, EMAIL_PASSWORD, FARMER_PHONE)
        self.log_file = "irrigation_log.csv"
        self.last_manual_check = 0
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("timestamp,soil_moisture,temperature,humidity,raindrop,rainfall_1d,rainfall_3d,water_amount,mode,crop_type,is_manual\n")
    
    def offline_prediction(self, soil_moisture, temperature, humidity, raindrop):
        """Fallback prediction when model or weather API fails"""
        profile = CROP_PROFILES[self.crop_type]
        water_needed = (profile["ideal_moisture"] - soil_moisture) * profile["water_per_percent"]
        
        # Adjust for temperature (more water when hot)
        if temperature > profile["max_temp"]:
            water_needed += 5
        
        # Adjust for humidity (less water when humid)
        water_needed -= (humidity - 50) * 0.1
        
        # Adjust for raindrop sensor (less water when rain detected)
        if raindrop > 50:  # High value means rain detected
            water_needed -= 10
            
        return max(0, water_needed)
    
    def adjust_for_rainfall(self, water_needed, rainfall_1d, rainfall_3d):
        """Adjust irrigation based on rainfall forecast"""
        profile = CROP_PROFILES[self.crop_type]
        
        # Reduce water if rain is coming soon
        if rainfall_1d > 5:  # Significant rain expected today/tomorrow
            water_needed -= rainfall_1d * 0.5  # Assume 50% of rain contributes to soil moisture
        
        # Add more water during dry spells
        if rainfall_3d < 5:  # Dry forecast for next 3 days
            water_needed += 5  # Buffer for dry conditions
            
        # Cap at bounds
        water_needed = max(0, water_needed)
        water_needed = min(water_needed, profile["max_water"])
        
        return water_needed
    
    def check_manual_irrigation(self):
        """Check if manual irrigation is requested and handle it"""
        # Check if enough time has passed since last check (every 30 seconds)
        current_time = time.time()
        if current_time - self.last_manual_check < 30:
            return False
            
        self.last_manual_check = current_time
        
        # Check ThingSpeak for manual irrigation request
        manual_mode, water_amount = self.thingspeak.check_manual_irrigation()
        
        if manual_mode and water_amount > 0:
            print(f"🖐️ Manual irrigation requested: {water_amount:.2f} liters")
            
            # Send irrigation command
            success = self.thingspeak.write_irrigation_command(water_amount, is_manual=True)
            
            if success:
                # Log the manual irrigation
                sensor_data = self.thingspeak.read_sensor_data() or {
                    "soil_moisture": 0, 
                    "temperature": 0, 
                    "humidity": 0, 
                    "raindrop": 0
                }
                
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
                
                # Send notification
                self.notifier.send_alert(f"Manual irrigation completed: {water_amount:.2f} liters")
            
            return True
        
        return False
    
    def log_data(self, data):
        """Log irrigation data to CSV file"""
        try:
            with open(self.log_file, "a") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_line = f"{timestamp},{data['soil_moisture']:.2f},{data['temperature']:.2f},"
                log_line += f"{data['humidity']:.2f},{data.get('raindrop', 0):.2f},"
                log_line += f"{data.get('rainfall_1d', 0):.2f},{data.get('rainfall_3d', 0):.2f},"
                log_line += f"{data['water_amount']:.2f},{data['mode']},{data['crop_type']},"
                log_line += f"{data.get('is_manual', 0)}\n"
                f.write(log_line)
        except Exception as e:
            print(f"Logging error: {e}")
            # Log errors to separate file
            with open("error_log.txt", "a") as f:
                f.write(f"{datetime.now()}: Logging error - {str(e)}\n")
    
    def run(self):
        """Main irrigation control loop"""
        print(f"🌿 GreenGuard Smart Irrigation System Running for {self.crop_type}...")
        print(f"Using ThingSpeak for data communication")
        print(f"Channel ID: {THINGSPEAK_CHANNEL_ID}")
        print(f"Manual irrigation control enabled")
        
        last_auto_check = 0
        auto_check_interval = 300  # 5 minutes between automatic checks
        
        while True:
            try:
                # First check for manual irrigation requests
                if self.check_manual_irrigation():
                    # If manual irrigation was performed, wait a bit before checking again
                    time.sleep(10)
                    continue
                
                # Only perform automatic irrigation check at the specified interval
                current_time = time.time()
                if current_time - last_auto_check < auto_check_interval:
                    # Sleep briefly then check for manual requests again
                    time.sleep(5)
                    continue
                    
                last_auto_check = current_time
                
                # 1. Get sensor data from ThingSpeak (data from ESP32)
                sensor_data = self.thingspeak.read_sensor_data()
                if not sensor_data:
                    self.notifier.send_alert("Sensor data not received from ThingSpeak! Check your ESP32 connection.")
                    time.sleep(60)  # Wait before retrying
                    continue
                
                soil_moisture = sensor_data.get("soil_moisture", 0)
                temperature = sensor_data.get("temperature", 0)
                humidity = sensor_data.get("humidity", 0)
                raindrop = sensor_data.get("raindrop", 0)
                
                # Validate sensor data with realistic ranges
                if not (0 <= soil_moisture <= 100) or \
                   not (0 <= temperature <= 50) or \
                   not (0 <= humidity <= 100) or \
                   not (0 <= raindrop <= 100):
                    error_msg = f"Invalid sensor readings detected! Moisture={soil_moisture:.1f}%, "
                    error_msg += f"Temp={temperature:.1f}°C, Humidity={humidity:.1f}%, "
                    error_msg += f"Raindrop={raindrop:.1f}%"
                    self.notifier.send_alert(error_msg)
                    
                    # Log error to separate file
                    with open("error_log.txt", "a") as f:
                        f.write(f"{datetime.now()}: {error_msg}\n")
                    
                    time.sleep(60)
                    continue
                
                # 2. Get weather forecast
                weather_data = self.weather.get_forecast()
                rainfall_1d = weather_data["rainfall_1d"]
                rainfall_3d = weather_data["rainfall_3d"]
                
                # 3. Determine irrigation amount using model or fallback
                if weather_data["success"]:
                    # Use ML model with all data as DataFrame to avoid feature name warning
                    input_features = pd.DataFrame([[
                        soil_moisture, 
                        temperature, 
                        humidity, 
                        rainfall_1d,
                        rainfall_3d,
                        raindrop
                    ]], columns=["soil_moisture", "temperature", "humidity", "rainfall_1d", "rainfall_3d", "raindrop"])
                    water_needed = self.model.predict(input_features)
                    prediction_mode = "ML-Model"
                else:
                    # Fallback to rule-based prediction
                    water_needed = self.offline_prediction(soil_moisture, temperature, humidity, raindrop)
                    prediction_mode = "Fallback"
                
                # 4. Adjust for rainfall forecast
                final_water = self.adjust_for_rainfall(water_needed, rainfall_1d, rainfall_3d)
                
                # 5. Send irrigation command to ThingSpeak if needed
                if final_water > 0:
                    print(f"🌧️ Irrigation needed: {final_water:.2f}L ({prediction_mode})")
                    print(f"📊 Data: Moisture={soil_moisture:.1f}%, Temp={temperature:.1f}°C, Humidity={humidity:.1f}%")
                    print(f"🌦️ Forecast: Rain today={rainfall_1d:.1f}mm, 3-day={rainfall_3d:.1f}mm")
                    
                    # Send command to ThingSpeak
                    self.thingspeak.write_irrigation_command(final_water, is_manual=False)
                else:
                    print(f"✅ No irrigation needed. Soil moisture: {soil_moisture:.1f}%")
                
                # 6. Log data
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
                
                # Wait a bit before checking for manual requests again
                print(f"Next automatic check in {auto_check_interval//60} minutes...")
                
            except KeyboardInterrupt:
                print("Irrigation system stopped by user")
                break
            except Exception as e:
                print(f"Error in irrigation cycle: {e}")
                self.notifier.send_alert(f"System error: {str(e)}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    # Start the irrigation controller
    controller = IrrigationController(crop_type="wheat")
    controller.run()
