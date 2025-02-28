# created by Mushfiq
# created by Mushfiq
# created by Mushfiq
# created by Mushfiq

import subprocess
import sys
import os
import time
import shutil
from pathlib import Path

def print_banner(message):
    print("=" * 80)
    print(message.center(80))
    print("=" * 80)

def print_step(step_num, message):
    print(f"\n🔷 Step {step_num}: {message}")

def run_command(command, description=None):
    if description:
        print(f"\n⚙️  {description}...")
    
    try:
        process = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        return False

def main():
    print_banner("GreenGuard Smart Irrigation System Setup")
    print("\nThis script will help you set up the GreenGuard system.")
    
    # Check Python version
    print_step(1, "Checking Python version")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return
    print("✅ Python version OK")
    
    # Check if we're running on a Raspberry Pi
    print_step(2, "Checking system")
    is_raspberry_pi = os.path.exists('/proc/device-tree/model') and 'Raspberry Pi' in open('/proc/device-tree/model').read()
    
    if is_raspberry_pi:
        print("✅ Running on Raspberry Pi")
    else:
        print("⚠️ Not running on Raspberry Pi. Some functionality may be limited.")
    
    # Install required Python packages
    print_step(3, "Installing Python dependencies")
    requirements = [
        "flask",
        "flask-cors",
        "pandas",
        "numpy",
        "scikit-learn",
        "joblib",
        "requests"
    ]
    
    if is_raspberry_pi:
        requirements.append("RPi.GPIO")
    
    packages_str = " ".join(requirements)
    if run_command(f"{sys.executable} -m pip install {packages_str}", "Installing Python packages"):
        print("✅ Python dependencies installed successfully")
    else:
        print("❌ Failed to install all Python dependencies")
        return
    
    # Check if the model exists or needs to be trained
    print_step(4, "Checking for trained model")
    model_exists = os.path.exists('irrigation_model.pkl')
    
    if model_exists:
        print("✅ Trained model found")
    else:
        print("⚠️ No trained model found")
        if input("Would you like to train the model now? (y/n): ").lower() == 'y':
            if os.path.exists('train_model.py'):
                if run_command(f"{sys.executable} train_model.py", "Training model"):
                    print("✅ Model training completed")
                else:
                    print("❌ Model training failed")
            else:
                print("❌ train_model.py not found")
                return
        else:
            print("⚠️ Continuing without training the model. The system will use mock data.")
    
    # Start the backend server
    print_step(5, "Starting the backend server")
    print("The backend server will be started. Press Ctrl+C to stop.")
    print("Backend API will be available at: http://localhost:8000")
    
    if input("Start the backend server now? (y/n): ").lower() == 'y':
        try:
            subprocess.run([sys.executable, "main.py"], check=True)
        except KeyboardInterrupt:
            print("\n⚠️ Backend server stopped")
    else:
        print("\nBackend server not started. You can start it manually with:")
        print(f"    {sys.executable} main.py")
    
    print_banner("Setup Complete!")
    print("\nTo start the backend server manually:")
    print(f"    {sys.executable} main.py")
    print("\nMake sure your frontend is configured to connect to http://localhost:8000")
    print("If running on a different device, use the IP address of this machine instead of localhost")

if __name__ == "__main__":
    main()
