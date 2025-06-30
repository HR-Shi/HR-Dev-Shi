import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface EngagementChartProps {
  data: Array<{
    month: string;
    engagement: number;
  }>;
}

export function EngagementChart({ data }: EngagementChartProps) {
  const maxValue = Math.max(...data.map(d => d.engagement));
  
  return (
    <div className="w-full h-64">
      <div className="flex items-end justify-between h-full space-x-2">
        {data.map((item, index) => (
          <div key={index} className="flex flex-col items-center flex-1">
            <div className="w-full bg-gray-200 rounded-t-md relative" style={{ height: '200px' }}>
              <div
                className="bg-blue-500 rounded-t-md absolute bottom-0 w-full transition-all duration-300"
                style={{ height: `${(item.engagement / maxValue) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-2 text-center">{item.month}</p>
            <p className="text-sm font-semibold text-gray-900">{item.engagement}%</p>
          </div>
        ))}
      </div>
    </div>
  );
}