
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Wheat } from "lucide-react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from "recharts";

interface IrrigationRecord {
  date: string;
  actual_water: number;
  predicted_water: number;
}

interface IrrigationHistoryChartProps {
  data: IrrigationRecord[];
}

const IrrigationHistoryChart = ({ data }: IrrigationHistoryChartProps) => {
  return (
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
            data={data.slice(0, 7).reverse()}
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
  );
};

export default IrrigationHistoryChart;
