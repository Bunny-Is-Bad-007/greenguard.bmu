
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sun } from "lucide-react";

interface WeatherCardProps {
  weatherData: {
    temp: number;
    humidity: number;
    description: string;
    wind_speed: number;
    icon: string;
  } | null;
}

const WeatherCard = ({ weatherData }: WeatherCardProps) => {
  return (
    <Card className="glass-card">
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
  );
};

export default WeatherCard;
