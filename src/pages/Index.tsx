
import React from 'react';
import { Card } from "@/components/ui/card";
import { Droplet, ThermometerSun, Wind, Timer } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Slider } from "@/components/ui/slider";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { useQuery } from "@tanstack/react-query";

const mockWeatherData = [
  { time: "Mon", temperature: 24, rainfall: 0 },
  { time: "Tue", temperature: 26, rainfall: 10 },
  { time: "Wed", temperature: 25, rainfall: 5 },
  { time: "Thu", temperature: 27, rainfall: 0 },
  { time: "Fri", temperature: 23, rainfall: 15 },
];

const mockIrrigationHistory = [
  { date: "2024-02-01", amount: 50, suggested: 45 },
  { date: "2024-02-02", amount: 40, suggested: 40 },
  { date: "2024-02-03", amount: 60, suggested: 55 },
  { date: "2024-02-04", amount: 45, suggested: 45 },
];

// API functions
const fetchIrrigationHistory = async () => {
  const response = await fetch('http://localhost:8000/history');
  if (!response.ok) {
    throw new Error('Failed to fetch irrigation history');
  }
  return response.json();
};

const requestIrrigation = async (waterLevel: number) => {
  const response = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      soil_moisture: 67, // Replace with actual sensor reading
      temperature: 24,   // Replace with actual sensor reading
      humidity: 45,      // Replace with actual sensor reading
      rainfall_forecast: 0,
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

  // Fetch irrigation history
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['irrigationHistory'],
    queryFn: fetchIrrigationHistory,
  });

  const handleIrrigationStart = async () => {
    try {
      const prediction = await requestIrrigation(manualWaterLevel[0]);
      toast({
        title: "Irrigation Started",
        description: `Dispensing ${manualWaterLevel[0]} liters of water. AI recommended: ${prediction.recommended_water}L`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start irrigation. Please try again.",
        variant: "destructive",
      });
    }
  };

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
              <Droplet className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Soil Moisture</p>
              <p className="text-2xl font-semibold">67%</p>
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
              <p className="text-2xl font-semibold">24°C</p>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-full">
              <Wind className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Humidity</p>
              <p className="text-2xl font-semibold">45%</p>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-full">
              <Timer className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Next Watering</p>
              <p className="text-2xl font-semibold">2h 15m</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="glass-card p-6 col-span-2">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Pump Status</span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                Active
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Water Pressure</span>
              <span className="text-gray-900">45 PSI</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Battery Level</span>
              <span className="text-gray-900">85%</span>
            </div>
          </div>
        </Card>

        <Card className="glass-card p-6">
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
                className="glass-button w-full py-2 px-4"
              >
                Start Manual Irrigation
              </button>
              <button
                className="glass-button w-full py-2 px-4 disabled:opacity-50"
                disabled
              >
                Stop Irrigation
              </button>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Weather Forecast</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockWeatherData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Line yAxisId="left" type="monotone" dataKey="temperature" stroke="#8884d8" name="Temperature (°C)" />
                <Line yAxisId="right" type="monotone" dataKey="rainfall" stroke="#82ca9d" name="Rainfall (mm)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Irrigation History</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockIrrigationHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="amount" fill="#8884d8" name="Actual Amount (L)" />
                <Bar dataKey="suggested" fill="#82ca9d" name="AI Suggested (L)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Index;
