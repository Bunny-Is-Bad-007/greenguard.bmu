
import { Card } from "@/components/ui/card";
import { Droplet, ThermometerSun, Wind, Timer } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const { toast } = useToast();

  const handleIrrigationStart = () => {
    toast({
      title: "Irrigation Started",
      description: "The system is now dispensing water based on AI recommendations.",
    });
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
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-4">
            <button
              onClick={handleIrrigationStart}
              className="glass-button w-full py-2 px-4"
            >
              Start Irrigation
            </button>
            <button
              className="glass-button w-full py-2 px-4 disabled:opacity-50"
              disabled
            >
              Stop Irrigation
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Index;
