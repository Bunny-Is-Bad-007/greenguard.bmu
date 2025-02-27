
import React from 'react';
import { Card } from "@/components/ui/card";
import { Droplet, ThermometerSun, Wind, Timer, CloudRain, TrendingUp, History } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Slider } from "@/components/ui/slider";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, Area, AreaChart, ComposedChart } from "recharts";
import { useQuery } from "@tanstack/react-query";

// API functions
const fetchIrrigationHistory = async () => {
  const response = await fetch('http://127.0.0.1:8000/history');
  if (!response.ok) {
    throw new Error('Failed to fetch irrigation history');
  }
  return response.json();
};

const requestIrrigation = async (soilMoisture: number, temperature: number) => {
  const response = await fetch('http://127.0.0.1:8000/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      soil_moisture: soilMoisture,
      temperature: temperature
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get irrigation prediction');
  }
  return response.json();
};

const Index = () => {
  const { toast } = useToast();
  const maxWaterLevel = 100;
  const [manualWaterLevel, setManualWaterLevel] = React.useState([50]);
  const [isIrrigating, setIsIrrigating] = React.useState(false);
  const [currentPrediction, setCurrentPrediction] = React.useState<any>(null);
  
  // Current sensor readings - you can make these state variables if they're dynamic
  const currentSoilMoisture = 30;
  const currentTemperature = 28;

  // Fetch irrigation history
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['irrigationHistory'],
    queryFn: fetchIrrigationHistory,
  });

  const handleIrrigationStart = async () => {
    try {
      setIsIrrigating(true);
      const prediction = await requestIrrigation(currentSoilMoisture, currentTemperature);
      setCurrentPrediction(prediction);
      
      toast({
        title: "Irrigation Started",
        description: prediction.decision || `AI Model Recommendation: ${prediction.predicted_water}L. Manual setting: ${manualWaterLevel[0]}L`,
      });
      
      console.log("🚀 AI Prediction:", prediction);
    } catch (error) {
      console.error("❌ API Error:", error);
      toast({
        title: "Error",
        description: "Failed to start irrigation. Please try again.",
        variant: "destructive",
      });
    } finally {
      // In a real app, this would be controlled by feedback from the irrigation system
      setTimeout(() => setIsIrrigating(false), 5000);
    }
  };

  // Transform rain_info into chart data if available
  const rainfallForecastData = currentPrediction?.rain_info?.map((info: string) => {
    const [date, amount] = info.split(": ");
    return {
      date: date.split(" ")[0], // Keep only the date part
      rainfall: parseFloat(amount.replace(" mm", "")),
    };
  }) || [];

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-green-50 to-blue-50">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2 animate-fade-in">GreenGuard</h1>
        <p className="text-lg text-gray-600 animate-fade-in">Smart Irrigation System</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Droplet className={`w-6 h-6 text-blue-600 ${isIrrigating ? 'animate-pulse' : ''}`} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Soil Moisture</p>
              <p className="text-2xl font-semibold">{currentSoilMoisture}%</p>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-100 rounded-full">
              <ThermometerSun className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Temperature</p>
              <p className="text-2xl font-semibold">{currentTemperature}°C</p>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-full">
              <CloudRain className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Forecast Rain</p>
              <p className="text-2xl font-semibold">
                {currentPrediction?.rainfall_forecast?.toFixed(1) || "0"} mm
              </p>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-full">
              <History className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Irrigation</p>
              <p className="text-2xl font-semibold">
                {historyData?.history?.[0]?.actual_water || 0}L
              </p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Irrigation Status</span>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                isIrrigating ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {isIrrigating ? 'Active' : 'Idle'}
              </span>
            </div>
            {currentPrediction && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">AI Recommendation</span>
                <span className="text-gray-900">{currentPrediction.predicted_water}L</span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-gray-600">System Health</span>
              <span className="text-gray-900">Optimal</span>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6 col-span-2">
          <h2 className="text-xl font-semibold mb-4">Manual Control</h2>
          <div className="space-y-6">
            <div>
              <label className="text-sm text-gray-600 mb-2 block">
                Water Level (Liters): {manualWaterLevel[0]}
              </label>
              <Slider
                value={manualWaterLevel}
                onValueChange={setManualWaterLevel}
                max={maxWaterLevel}
                step={1}
                className="mb-4"
              />
              <p className="text-xs text-gray-500">
                Maximum allowed: {maxWaterLevel}L
              </p>
            </div>
            <div className="space-y-3">
              <button
                onClick={handleIrrigationStart}
                disabled={isIrrigating}
                className={`glass-button w-full py-2 px-4 ${
                  isIrrigating ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isIrrigating ? '💧 Irrigating...' : 'Start Manual Irrigation'}
              </button>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Rainfall Forecast</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={rainfallForecastData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="rainfall" fill="#82ca9d" stroke="#82ca9d" name="Rainfall (mm)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Irrigation History</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={historyData?.history || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="actual_water" fill="#8884d8" name="Actual Water (L)" />
                <Line type="monotone" dataKey="predicted_water" stroke="#82ca9d" name="AI Predicted (L)" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Index;
