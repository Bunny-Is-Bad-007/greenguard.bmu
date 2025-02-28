
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface SensorCardProps {
  title: string;
  value: string | number;
  unit?: string;
  description: string;
  icon: LucideIcon;
  iconColor: string;
  valueColor: string;
}

const SensorCard = ({
  title,
  value,
  unit = "",
  description,
  icon: Icon,
  iconColor,
  valueColor,
}: SensorCardProps) => {
  return (
    <Card className="glass-card">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-bold">{title}</CardTitle>
        <Icon className={`h-5 w-5 ${iconColor}`} />
      </CardHeader>
      <CardContent>
        <div className={`text-3xl font-bold ${valueColor}`}>
          {value}
          {unit}
        </div>
        <CardDescription>{description}</CardDescription>
      </CardContent>
    </Card>
  );
};

export default SensorCard;
