import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { DOMAIN_COLORS } from "../../utils/gameMechanics";

interface DomainPieChartProps {
  data: Array<{ domain: string; value: number; color: string }>;
}

const COLORS: Record<string, string> = {
  fitness: "#ef4444",
  productivity: "#3b82f6",
  learning: "#a855f7",
};

export default function DomainPieChart({ data }: DomainPieChartProps) {
  if (data.every((d) => d.value === 0)) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-400 text-sm">
        No data available
      </div>
    );
  }

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ domain, percent }) => `${domain} ${(percent * 100).toFixed(0)}%`}
            outerRadius={60}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry) => (
              <Cell key={entry.domain} fill={COLORS[entry.domain]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #6366f1",
              borderRadius: "8px",
            }}
          />
          <Legend verticalAlign="bottom" height={36} iconType="circle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
