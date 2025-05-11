import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, HeatMapGrid, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { Card, Row, Col, Statistic, Alert, Spin, Tabs, Button, Space, Badge, Progress } from 'antd';
import { 
  ClockCircleOutlined, AlertOutlined, CheckCircleOutlined,
  DashboardOutlined, LineChartOutlined, BarChartOutlined,
  ReloadOutlined, SettingOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;

const PerformanceDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('1h');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get(`/api/metrics/dashboard?timeRange=${timeRange}`);
        setMetrics(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load metrics');
        setLoading(false);
      }
    };

    fetchMetrics();
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchMetrics, 30000);
    }
    return () => clearInterval(interval);
  }, [timeRange, autoRefresh]);

  const handleRefresh = () => {
    setLoading(true);
    fetchMetrics();
  };

  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high': return '#ff4d4f';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#1890ff';
    }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <Spin size="large" />
      <p>Loading dashboard data...</p>
    </div>
  );
  
  if (error) return (
    <Alert
      type="error"
      message="Error"
      description={error}
      action={
        <Button type="primary" onClick={handleRefresh}>
          Retry
        </Button>
      }
    />
  );
  
  if (!metrics) return null;

  return (
    <div className="performance-dashboard" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1><DashboardOutlined /> System Performance Dashboard</h1>
        <Space>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={handleRefresh}
            loading={loading}
          >
            Refresh
          </Button>
          <Button 
            icon={<SettingOutlined />}
            onClick={() => setAutoRefresh(!autoRefresh)}
            type={autoRefresh ? 'primary' : 'default'}
          >
            Auto Refresh {autoRefresh ? 'On' : 'Off'}
          </Button>
        </Space>
      </div>

      <Tabs defaultActiveKey="overview">
        <TabPane tab={<span><DashboardOutlined />Overview</span>} key="overview">
          {/* Key Metrics */}
          <Row gutter={[16, 16]} className="metrics-row">
            <Col xs={24} sm={12} md={8}>
              <Card hoverable>
                <Statistic
                  title="Average Rule Match Time"
                  value={metrics.rule_match_time}
                  suffix="ms"
                  precision={2}
                  valueStyle={{ color: '#3f8600' }}
                  prefix={<CheckCircleOutlined />}
                />
                <Progress 
                  percent={Math.min(100, (metrics.rule_match_time / 1000) * 100)} 
                  showInfo={false}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <Card hoverable>
                <Statistic
                  title="LLM Explanation Time"
                  value={metrics.llm_time}
                  suffix="ms"
                  precision={2}
                  valueStyle={{ color: '#cf1322' }}
                  prefix={<ClockCircleOutlined />}
                />
                <Progress 
                  percent={Math.min(100, (metrics.llm_time / 2000) * 100)} 
                  showInfo={false}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#cf1322',
                  }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <Card hoverable>
                <Statistic
                  title="System Uptime"
                  value={formatUptime(metrics.uptime)}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
                <Progress 
                  percent={100} 
                  showInfo={false}
                  strokeColor="#1890ff"
                />
              </Card>
            </Col>
          </Row>

          {/* Top Alerts */}
          <Card 
            title={
              <span>
                <AlertOutlined /> Top 5 Triggered Alerts
                <Badge count={metrics.top_alerts.length} style={{ marginLeft: '8px' }} />
              </span>
            }
            className="alerts-card"
            style={{ marginTop: '24px' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              {metrics.top_alerts.map((alert, index) => (
                <Alert
                  key={index}
                  message={
                    <span>
                      <Badge color={getSeverityColor(alert.severity)} />
                      {alert.message}
                    </span>
                  }
                  description={
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Severity: {alert.severity}</span>
                      <span>Count: {alert.count}</span>
                    </div>
                  }
                  type={alert.severity === 'high' ? 'error' : 'warning'}
                  showIcon
                />
              ))}
            </Space>
          </Card>
        </TabPane>

        <TabPane tab={<span><LineChartOutlined />Performance Trends</span>} key="trends">
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card title="Rule Match Time Trend">
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={metrics.rule_match_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="time" 
                      stroke="#8884d8" 
                      fill="#8884d8" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col span={24}>
              <Card title="LLM Response Time Trend">
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={metrics.llm_time_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="time" 
                      stroke="#82ca9d" 
                      fill="#82ca9d" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={<span><BarChartOutlined />Feedback Analysis</span>} key="feedback">
          <Card title="Rule Feedback Heatmap" className="heatmap-card">
            <ResponsiveContainer width="100%" height={500}>
              <HeatMapGrid
                data={metrics.feedback_heatmap}
                xLabels={metrics.feedback_heatmap.xLabels}
                yLabels={metrics.feedback_heatmap.yLabels}
                cellRender={(x, y, value) => (
                  <div
                    style={{
                      backgroundColor: `rgba(255, 0, 0, ${value / 100})`,
                      padding: '8px',
                      textAlign: 'center',
                      borderRadius: '4px',
                      color: value > 50 ? 'white' : 'black',
                      transition: 'all 0.3s'
                    }}
                  >
                    {value}%
                  </div>
                )}
              />
            </ResponsiveContainer>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default PerformanceDashboard; 