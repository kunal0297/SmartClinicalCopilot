import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Box, Typography } from '@mui/material';
import type { BaseProps, ChartDataPoint } from '@/types/common';

interface AlertMetrics {
  topRules: Array<{
    rule_id: string;
    alert_count: number;
    override_count: number;
    override_rate: number;
  }>;
  totalAlerts: number;
  totalOverrides: number;
  overrideRate: number;
}

interface AlertMetricsChartProps extends BaseProps {
  metrics: AlertMetrics;
}

interface ChartData extends ChartDataPoint {
  alerts: number;
  overrides: number;
  overrideRate: number;
}

const AlertMetricsChart: React.FC<AlertMetricsChartProps> = ({ metrics, className }) => {
  // Transform metrics data for the chart
  const chartData = React.useMemo<ChartData[]>(() => {
    if (!metrics.topRules) return [];

    return metrics.topRules.map(rule => ({
      name: `Rule ${rule.rule_id}`,
      alerts: rule.alert_count,
      overrides: rule.override_count,
      overrideRate: rule.override_rate * 100
    }));
  }, [metrics]);

  return (
    <Box sx={{ width: '100%', height: 400 }} className={className}>
      <ResponsiveContainer>
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="alerts"
            stroke="#8884d8"
            name="Alerts"
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="overrides"
            stroke="#82ca9d"
            name="Overrides"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="overrideRate"
            stroke="#ffc658"
            name="Override Rate (%)"
          />
        </LineChart>
      </ResponsiveContainer>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="body2" color="text.secondary">
          Total Alerts: {metrics.totalAlerts}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Total Overrides: {metrics.totalOverrides}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Overall Override Rate: {(metrics.overrideRate * 100).toFixed(1)}%
        </Typography>
      </Box>
    </Box>
  );
};

export default AlertMetricsChart; 