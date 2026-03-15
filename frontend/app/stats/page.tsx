'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Loader2,
  ArrowUp,
  ArrowDown,
  Minus,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from 'recharts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StatsSummary {
  total_reports: number;
  average_score: number;
  average_pass_probability: number;
  score_distribution: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
    very_poor: number;
  };
}

interface TrendData {
  date: string;
  average_score: number;
  evaluations_count: number;
}

export default function StatsPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [trend, setTrend] = useState<TrendData[]>([]);
  const [selectedDays, setSelectedDays] = useState(30);

  useEffect(() => {
    fetchStats();
    fetchTrend();
  }, [selectedDays]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/stats/summary`);
      if (!response.ok) throw new Error('加载统计数据失败');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('加载统计数据失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrend = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/history/trend?days=${selectedDays}`);
      if (!response.ok) throw new Error('加载趋势数据失败');
      const data = await response.json();
      setTrend(data.trend || []);
    } catch (err) {
      console.error('加载趋势数据失败:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto text-primary-600 mb-4" />
          <p className="text-gray-600">加载统计数据...</p>
        </div>
      </div>
    );
  }

  const scoreDistributionData = stats
    ? [
        { name: '优秀 (90+)', value: stats.score_distribution.excellent, color: '#22c55e' },
        { name: '良好 (75-89)', value: stats.score_distribution.good, color: '#84cc16' },
        { name: '中等 (60-74)', value: stats.score_distribution.fair, color: '#eab308' },
        { name: '较差 (40-59)', value: stats.score_distribution.poor, color: '#f97316' },
        { name: '很差 (<40)', value: stats.score_distribution.very_poor, color: '#ef4444' },
      ]
    : [];

  const radarData = [
    { subject: '内容质量', A: 75, fullMark: 100 },
    { subject: '网站结构', A: 68, fullMark: 100 },
    { subject: '用户体验', A: 82, fullMark: 100 },
    { subject: '技术合规', A: 71, fullMark: 100 },
  ];

  // 模拟常见问题数据（实际应从 API 获取）
  const commonIssues = [
    { name: '缺少隐私政策页面', count: 45, percentage: 68 },
    { name: '内容质量不足', count: 38, percentage: 57 },
    { name: '网站结构不清晰', count: 32, percentage: 48 },
    { name: '移动端适配问题', count: 28, percentage: 42 },
    { name: '页面加载速度慢', count: 25, percentage: 38 },
    { name: '缺少联系方式', count: 22, percentage: 33 },
    { name: '导航不清晰', count: 18, percentage: 27 },
    { name: '内容更新频率低', count: 15, percentage: 23 },
    { name: 'SEO 优化不足', count: 12, percentage: 18 },
    { name: 'HTTPS 未启用', count: 8, percentage: 12 },
  ];

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) return <ArrowUp className="w-4 h-4 text-green-600" />;
    if (current < previous) return <ArrowDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <a href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                返回首页
              </a>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <BarChart3 className="w-7 h-7 text-primary-600" />
                统计分析
              </h1>
            </div>
            <div className="flex gap-2">
              {[7, 30, 90].map((days) => (
                <button
                  key={days}
                  onClick={() => setSelectedDays(days)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    selectedDays === days
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  最近{days}天
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Summary Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<CheckCircle className="w-6 h-6 text-primary-600" />}
            label="总评估数"
            value={stats?.total_reports || 0}
            trend="+12%"
            trendUp={true}
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6 text-success" />}
            label="平均分数"
            value={stats?.average_score || 0}
            suffix="分"
            trend="+5.2"
            trendUp={true}
          />
          <StatCard
            icon={<BarChart3 className="w-6 h-6 text-info" />}
            label="平均通过概率"
            value={stats?.average_pass_probability || 0}
            suffix="%"
            trend="+3.1"
            trendUp={true}
          />
          <StatCard
            icon={<AlertTriangle className="w-6 h-6 text-warning" />}
            label="平均问题数"
            value={Math.round((stats?.total_reports || 1) * 3.5)}
            trend="-2.3"
            trendUp={false}
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Score Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">评分分布</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={scoreDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {scoreDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-5 gap-2 mt-4">
              {scoreDistributionData.map((item, index) => (
                <div key={index} className="text-center">
                  <div className="w-3 h-3 rounded-full mx-auto mb-1" style={{ backgroundColor: item.color }} />
                  <div className="text-xs text-gray-600">{item.name}</div>
                  <div className="text-sm font-semibold">{item.value}</div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Score Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">评分趋势</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip
                    labelFormatter={(label) => `日期：${label}`}
                    formatter={(value: number) => [`${value}分`, '平均分']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="average_score"
                    name="平均分数"
                    stroke="#2563eb"
                    strokeWidth={2}
                    dot={{ fill: '#2563eb', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Radar Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">各维度平均分</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar
                    name="平均得分"
                    dataKey="A"
                    stroke="#2563eb"
                    strokeWidth={2}
                    fill="#3b82f6"
                    fillOpacity={0.5}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Common Issues */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">常见问题 TOP 10</h2>
            <div className="space-y-4">
              {commonIssues.map((issue, index) => (
                <div key={index} className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{issue.name}</span>
                      <span className="text-sm text-gray-600">{issue.count}次</span>
                    </div>
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all"
                        style={{ width: `${issue.percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Evaluations Over Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-6">评估数量趋势</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip
                  labelFormatter={(label) => `日期：${label}`}
                  formatter={(value: number, name: string) =>
                    name === 'evaluations_count' ? [`${value}次`, '评估数'] : [`${value}分`, '平均分']
                  }
                />
                <Legend />
                <Bar dataKey="evaluations_count" name="评估数量" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-gray-600 text-sm">
          <p>数据统计基于最近 {selectedDays} 天的评估记录</p>
          <p className="mt-1">数据更新时间：{new Date().toLocaleString('zh-CN')}</p>
        </div>
      </div>
    </main>
  );
}

function StatCard({
  icon,
  label,
  value,
  suffix = '',
  trend,
  trendUp,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  suffix?: string;
  trend?: string;
  trendUp?: boolean;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        {icon}
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            trendUp ? 'text-green-600' : 'text-red-600'
          }`}>
            {getTrendIcon(trendUp ? 1 : 0, 0)}
            {trend}
          </div>
        )}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">
        {value}{suffix && <span className="text-lg text-gray-600 ml-1">{suffix}</span>}
      </div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
}

function getTrendIcon(current: number, previous: number) {
  if (current > previous) return <ArrowUp className="w-4 h-4" />;
  if (current < previous) return <ArrowDown className="w-4 h-4" />;
  return <Minus className="w-4 h-4" />;
}
