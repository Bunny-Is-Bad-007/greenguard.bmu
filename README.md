# 🌱 GreenGuard: AI-Powered Smart Irrigation System

**GreenGuard** is an **AI-powered irrigation system** that optimizes water usage by analyzing **soil moisture, temperature, and weather forecasts**. It helps prevent overwatering and conserves water for sustainable agriculture.

## 🚀 Features
- **Real-time sensor data monitoring** (soil moisture, temperature)
- **AI-based irrigation prediction**
- **Weather forecast integration** (rainfall, humidity, wind speed)
- **Manual & automatic irrigation control**
- **Water usage history & analytics**
- **User-friendly UI built with Vite + React + Tailwind CSS**

## 🛠️ Tech Stack
- **Frontend:** Vite + React + TypeScript + Tailwind CSS + shadcn-ui
- **Backend:** FastAPI (Python) with Uvicorn
- **Database:** (Optional) SQLite/PostgreSQL for storing irrigation history
- **Hardware:** ESP8266/LoRa + Raspberry Pi Zero (sensor data collection)
- **APIs:** OpenWeather API for real-time weather forecasting

---

## ⚡ Installation & Setup

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/Bunny-Is-Bad-007/greenguard.lpu.git
cd greenguard.lpu
```

### 2️⃣ **Backend Setup (FastAPI)**
```sh
cd backend
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate      # For Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
✅ **FastAPI running at:** `http://127.0.0.1:8000/`

---

### 3️⃣ **Frontend Setup (Vite + React)**
```sh
cd frontend
npm install
npm run dev
```
✅ **Vite UI running at:** `http://localhost:5173/`

---

## 🔗 API Endpoints

### **🌿 Predict Irrigation Needs**
```http
POST /predict
Content-Type: application/json
{
    "soil_moisture": 30,
    "temperature": 28
}
```
🔹 **Response:**
```json
{
    "predicted_water": 10.05,
    "rainfall_forecast": 32.61,
    "decision": "💧 Less Water Needed: 10.05 liters (Rain forecasted)"
}
```

### **📜 Get Irrigation History**
```http
GET /history
```
🔹 **Response:**
```json
{
    "history": [
        { "date": "2025-02-25", "actual_water": 45, "predicted_water": 42 },
        { "date": "2025-02-24", "actual_water": 50, "predicted_water": 48 }
    ]
}
```

### **⛅ Get Live Weather Data**
Use the OpenWeather API:
```http
GET https://api.openweathermap.org/data/2.5/weather?lat=31.3260&lon=75.5762&appid=YOUR_API_KEY&units=metric
```

---

## 🚀 Deployment Guide

### **1️⃣ Deploy FastAPI Backend**
- **Using Railway/Vercel Backend:**
```sh
railway up
```
- **Using DigitalOcean/AWS:**
```sh
docker-compose up -d
```

### **2️⃣ Deploy Frontend (Vercel)**
- **Import your GitHub repo on [Vercel](https://vercel.com/)**
- **Select `Vite` framework preset**
- **Set:**
  - **Build Command:** `npm run build`
  - **Output Directory:** `dist`
- **Click Deploy**

✅ **Your UI will be live at:**  
```
https://greenguard.vercel.app/
```

---

## 📌 To-Do List
- [ ] **Add AI model improvements**
- [ ] **Enhance UI with real-time charts**
- [ ] **Integrate LoRa sensor communication**
- [ ] **Deploy backend for public access**

---

## 💡 Contributing
Want to improve **GreenGuard**? PRs are welcome!  
1. Fork the repo  
2. Create a branch (`feature-xyz`)  
3. Commit & push changes  
4. Open a PR  

---

## 🤝 Contact
📧 **Email:** mushfiqul.alam.17.com   
🔗 **Website:** https://greenguard-lpu.vercel.app/

---

