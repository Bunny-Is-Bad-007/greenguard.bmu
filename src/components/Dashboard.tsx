
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Droplet, ThermometerSun, CloudRain, TrendingUp, History, Sun, Wheat } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/use-toast";
import { Separator } from "@/components/ui/separator";
import { AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Bar } from "recharts";

interface SensorData {
  soil_moisture: number;
  temperature: number;
}

interface PredictionResponse {
  predicted_water: number;
  rainfall_forecast: number;
  decision: string;
}

interface IrrigationRecord {
  date: string;
  actual_water: number;
  predicted_water: number;
}

interface WeatherData {
  temp: number;
  humidity: number;
  description: string;
  wind_speed: number;
  icon: string;
}

const Dashboard = () => {
  const [sensorData, setSensorData] = useState<SensorData>({
    soil_moisture: 30,
    temperature: 28,
  });
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [isIrrigating, setIsIrrigating] = useState(false);
  const [manualWaterAmount, setManualWaterAmount] = useState([30]);
  const [irrigationHistory, setIrrigationHistory] = useState<IrrigationRecord[]>([]);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch irrigation history from API
  const fetchIrrigationHistory = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/history");
      if (!response.ok) throw new Error("Failed to fetch irrigation history");
      const data = await response.json();
      setIrrigationHistory(data.history);
      console.log("✅ History fetched:", data.history);
    } catch (error) {
      console.error("❌ Error fetching history:", error);
      // Use mock data if API fails
      setIrrigationHistory([
        { date: "2025-02-25", actual_water: 45, predicted_water: 42 },
        { date: "2025-02-24", actual_water: 50, predicted_water: 48 },
        { date: "2025-02-23", actual_water: 38, predicted_water: 35 },
        { date: "2025-02-22", actual_water: 42, predicted_water: 40 },
        { date: "2025-02-21", actual_water: 55, predicted_water: 52 },
      ]);
    }
  };

  // Fetch weather data from OpenWeather API
  const fetchWeatherData = async () => {
    try {
      // Replace with your API key and coordinates
      const apiKey = "demo_key"; // Replace with actual API key
      const lat = "31.3260";
      const lon = "75.5762";
      const response = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`
      );
      
      if (!response.ok) throw new Error("Failed to fetch weather data");
      
      const data = await response.json();
      setWeatherData({
        temp: data.main.temp,
        humidity: data.main.humidity,
        description: data.weather[0].description,
        wind_speed: data.wind.speed,
        icon: data.weather[0].icon,
      });
      console.log("✅ Weather fetched:", data);
    } catch (error) {
      console.error("❌ Error fetching weather:", error);
      // Mock weather data
      setWeatherData({
        temp: 28.5,
        humidity: 60,
        description: "Clear sky",
        wind_speed: 3.5,
        icon: "01d",
      });
    }
  };

  // Predict irrigation needs based on sensor data
  const predictIrrigation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sensorData),
      });
      
      if (!response.ok) throw new Error("Failed to predict irrigation needs");
      
      const data = await response.json();
      setPrediction(data);
      console.log("🚀 Prediction:", data);
      toast({
        title: "Prediction Complete",
        description: data.decision,
      });
    } catch (error) {
      console.error("❌ Error predicting irrigation:", error);
      // Mock prediction data
      setPrediction({
        predicted_water: 10.05,
        rainfall_forecast: 32.61,
        decision: "💧 Less Water Needed: 10.05 liters (Rain forecasted)",
      });
      toast({
        title: "Using Mock Data",
        description: "Could not connect to API, using simulated values",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Start manual irrigation
  const startManualIrrigation = () => {
    setIsIrrigating(true);
    
    toast({
      title: "Irrigation Started",
      description: `Dispensing ${manualWaterAmount[0]} liters of water`,
    });
    
    // Simulate irrigation completion after 3 seconds
    setTimeout(() => {
      setIsIrrigating(false);
      
      // Update history with new irrigation record
      const newRecord: IrrigationRecord = {
        date: new Date().toISOString().split("T")[0],
        actual_water: manualWaterAmount[0],
        predicted_water: prediction?.predicted_water || manualWaterAmount[0],
      };
      
      setIrrigationHistory([newRecord, ...irrigationHistory]);
      
      toast({
        title: "Irrigation Complete",
        description: `Dispensed ${manualWaterAmount[0]} liters of water`,
      });
    }, 3000);
  };

  // Initial data fetch
  useEffect(() => {
    fetchIrrigationHistory();
    fetchWeatherData();
    predictIrrigation();

    // Refresh data every 5 minutes
    const interval = setInterval(() => {
      fetchWeatherData();
      fetchIrrigationHistory();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Get last irrigation data
  const lastIrrigation = irrigationHistory.length > 0 ? irrigationHistory[0] : null;

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Soil Moisture Card */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xl font-bold">Soil Moisture</CardTitle>
            <Droplet className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{sensorData.soil_moisture}%</div>
            <CardDescription>Current soil moisture level</CardDescription>
          </CardContent>
        </Card>

        {/* Temperature Card */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xl font-bold">Temperature</CardTitle>
            <ThermometerSun className="h-5 w-5 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-500">{sensorData.temperature}°C</div>
            <CardDescription>Current field temperature</CardDescription>
          </CardContent>
        </Card>

        {/* Rainfall Forecast Card */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xl font-bold">Rainfall</CardTitle>
            <CloudRain className="h-5 w-5 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {prediction?.rainfall_forecast.toFixed(1) || "0.0"} mm
            </div>
            <CardDescription>Expected rainfall in next 24h</CardDescription>
          </CardContent>
        </Card>

        {/* Last Irrigation Card */}
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xl font-bold">Last Irrigation</CardTitle>
            <History className="h-5 w-5 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {lastIrrigation ? `${lastIrrigation.actual_water}L` : "N/A"}
            </div>
            <CardDescription>
              {lastIrrigation ? `On ${lastIrrigation.date}` : "No recent irrigation"}
            </CardDescription>
          </CardContent>
        </Card>
      </div>

      {/* Weather and Irrigation Control Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Weather Card */}
        <Card className="glass-card md:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="h-5 w-5 text-yellow-500" />
              Weather Conditions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {weatherData ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center">
                  {weatherData.icon && (
                    <img
                      src={`https://openweathermap.org/img/wn/${weatherData.icon}@2x.png`}
                      alt={weatherData.description}
                      className="w-16 h-16"
                    />
                  )}
                  <div className="text-2xl font-bold">{weatherData.temp.toFixed(1)}°C</div>
                </div>
                <div className="text-center text-lg capitalize">{weatherData.description}</div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex flex-col items-center">
                    <span className="font-semibold">Humidity</span>
                    <span>{weatherData.humidity}%</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <span className="font-semibold">Wind</span>
                    <span>{weatherData.wind_speed} m/s</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-32">Loading weather data...</div>
            )}
          </CardContent>
        </Card>

        {/* Irrigation Control Card */}
        <Card className="glass-card md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Droplet className="h-5 w-5 text-blue-500" />
              Irrigation Control
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium mb-1 block">Water Amount (Liters)</label>
                <div className="flex items-center gap-4">
                  <Slider
                    defaultValue={[30]}
                    max={80}
                    step={1}
                    value={manualWaterAmount}
                    onValueChange={setManualWaterAmount}
                    className="flex-1"
                    disabled={isIrrigating}
                  />
                  <span className="text-lg font-semibold w-12 text-right">{manualWaterAmount[0]}L</span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  {prediction && (
                    <div className="text-sm">
                      <span className="font-semibold">AI Recommendation:</span>{" "}
                      <span className="text-green-600 font-bold">{prediction.predicted_water.toFixed(2)}L</span>
                    </div>
                  )}
                </div>
                <Button
                  onClick={startManualIrrigation}
                  className="glass-button px-6"
                  disabled={isIrrigating}
                >
                  {isIrrigating ? "Irrigating..." : "Start Manual Irrigation"}
                </Button>
              </div>

              {isIrrigating && (
                <div className="mt-4 animate-pulse">
                  <div className="h-2 bg-primary/20 rounded-full overflow-hidden">
                    <div className="h-full bg-primary animate-[water-flow_3s_ease-in-out_infinite]"></div>
                  </div>
                  <div className="text-center mt-2 text-green-600 font-semibold">
                    💧 Dispensing {manualWaterAmount[0]} liters of water...
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Rainfall Forecast Chart */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CloudRain className="h-5 w-5 text-blue-600" />
              Rainfall Forecast (Last 7 Days)
            </CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={[
                  { date: "Day 1", rainfall: 5.2 },
                  { date: "Day 2", rainfall: 8.5 },
                  { date: "Day 3", rainfall: 12.1 },
                  { date: "Day 4", rainfall: 6.8 },
                  { date: "Day 5", rainfall: 2.3 },
                  { date: "Day 6", rainfall: 0.5 },
                  { date: "Day 7", rainfall: prediction?.rainfall_forecast || 0 },
                ]}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis unit=" mm" />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="rainfall"
                  name="Rainfall"
                  stroke="#3182CE"
                  fill="#3182CE"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Irrigation History Chart */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wheat className="h-5 w-5 text-amber-600" />
              Irrigation History
            </CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={irrigationHistory.slice(0, 7).reverse()}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis unit="L" />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="actual_water"
                  name="Actual Water"
                  fill="#2E7D32"
                  barSize={20}
                />
                <Line
                  type="monotone"
                  dataKey="predicted_water"
                  name="Predicted Water"
                  stroke="#8D6F47"
                  strokeWidth={2}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Irrigation Records Table */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5 text-gray-600" />
            Recent Irrigation Records
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-green-50">
                  <th className="border border-gray-200 px-4 py-2 text-left">Date</th>
                  <th className="border border-gray-200 px-4 py-2 text-left">Actual Water (L)</th>
                  <th className="border border-gray-200 px-4 py-2 text-left">Predicted Water (L)</th>
                  <th className="border border-gray-200 px-4 py-2 text-left">Difference</th>
                </tr>
              </thead>
              <tbody>
                {irrigationHistory.slice(0, 5).map((record, index) => (
                  <tr key={index} className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="border border-gray-200 px-4 py-2">{record.date}</td>
                    <td className="border border-gray-200 px-4 py-2">{record.actual_water}</td>
                    <td className="border border-gray-200 px-4 py-2">{record.predicted_water.toFixed(2)}</td>
                    <td className="border border-gray-200 px-4 py-2">
                      <span className={record.actual_water > record.predicted_water ? "text-red-500" : "text-green-500"}>
                        {(record.actual_water - record.predicted_water).toFixed(2)}L
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
