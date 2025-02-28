
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/use-toast";
import { Droplet } from "lucide-react";

interface IrrigationControlProps {
  predictedWater: number | null;
  onIrrigate: (amount: number) => void;
}

const IrrigationControl = ({ predictedWater, onIrrigate }: IrrigationControlProps) => {
  const [waterAmount, setWaterAmount] = useState([30]);
  const [isIrrigating, setIsIrrigating] = useState(false);

  const handleIrrigation = () => {
    setIsIrrigating(true);
    
    toast({
      title: "Irrigation Started",
      description: `Dispensing ${waterAmount[0]} liters of water`,
    });
    
    // Simulate irrigation completion after 3 seconds
    setTimeout(() => {
      setIsIrrigating(false);
      onIrrigate(waterAmount[0]);
      
      toast({
        title: "Irrigation Complete",
        description: `Dispensed ${waterAmount[0]} liters of water`,
      });
    }, 3000);
  };

  return (
    <Card className="glass-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Droplet className="h-5 w-5 text-blue-500" />
          Manual Irrigation Control
        </CardTitle>
        <CardDescription>Adjust water amount and start irrigation manually</CardDescription>
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
                value={waterAmount}
                onValueChange={setWaterAmount}
                className="flex-1"
                disabled={isIrrigating}
              />
              <span className="text-lg font-semibold w-12 text-right">{waterAmount[0]}L</span>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div>
              {predictedWater !== null && (
                <div className="text-sm">
                  <span className="font-semibold">AI Recommendation:</span>{" "}
                  <span className="text-green-600 font-bold">{predictedWater.toFixed(2)}L</span>
                </div>
              )}
            </div>
            <Button
              onClick={handleIrrigation}
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
                💧 Dispensing {waterAmount[0]} liters of water...
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default IrrigationControl;
