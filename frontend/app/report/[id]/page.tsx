'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Download,
  Share2,
  CheckCircle,
  AlertTriangle,
  AlertCircle,
  Info,
  Lightbulb,
  TrendingUp,
  FileText,
  ExternalLink,
  Loader2,
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Metric {
  name: string;
  score: number;
  maxScore: number;
  weight: number;
}

interface Issue {
  id: string;
  category: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  recommendation: string;
}

interface AISuggestion {
  id: string;
  category: string;
  title: string;
  description: string;
  estimatedImpact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
}

interface ReportData {
  report_id: string;
  url: string;
  overall_score: number;
  pass_probability: number;
  metrics: Record<string, Metric>;
  issues: Issue[];
  ai_suggestions: AISuggestion[];
  rating: string;
  created_at: string;
  website_data?: any;
}

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/reports/${params.id}`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('报告不存在');
          }
          throw new Error('加载报告失败');
        }
        const data = await response.json();
        setReport(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchReport();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto text-primary-600 mb-4" />
          <p className="text-gray-600">加载报告中...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">加载失败</h2>
          <p className="text-gray-600 mb-6">{error || '报告不存在'}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  const radarData = Object.entries(report.metrics).map(([key, value]) => ({
    subject: getMetricName(key),
    A: value.score,
    fullMark: value.maxScore || 100,
  }));

  const COLORS = ['#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444'];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="w-5 h-5" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5" />;
      case 'low':
        return <Info className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    if (score >= 40) return 'bg-orange-100';
    return 'bg-red-100';
  };

  const exportReport = () => {
    // 简单实现：打印报告
    window.print();
  };

  const shareReport = async () => {
    const shareUrl = `${window.location.origin}/report/${report.report_id}`;
    try {
      await navigator.share({
        title: 'AdSense 评估报告',
        text: `网站 ${report.url} 的 AdSense 评估报告`,
        url: shareUrl,
      });
    } catch (err) {
      // 分享不支持时复制链接
      navigator.clipboard.writeText(shareUrl);
      alert('链接已复制到剪贴板');
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50 print:hidden">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              返回首页
            </button>
            <div className="flex gap-3">
              <button
                onClick={exportReport}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Download className="w-4 h-4" />
                导出报告
              </button>
              <button
                onClick={shareReport}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <Share2 className="w-4 h-4" />
                分享
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Report Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8"
        >
          <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
            {/* Score Display */}
            <div className="flex-shrink-0 text-center">
              <div className={`w-40 h-40 rounded-full ${getScoreBg(report.overall_score)} flex items-center justify-center mb-4`}>
                <div className={`text-5xl font-bold ${getScoreColor(report.overall_score)}`}>
                  {report.overall_score}
                </div>
              </div>
              <div className="text-lg font-semibold text-gray-900 mb-1">
                综合评分
              </div>
              <div className={`text-sm font-medium ${getScoreColor(report.overall_score)}`}>
                {report.rating}
              </div>
            </div>

            {/* Key Metrics */}
            <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                label="通过概率"
                value={`${Math.round(report.pass_probability)}%`}
                icon={<TrendingUp className="w-6 h-6 text-primary-600" />}
              />
              <MetricCard
                label="发现问题"
                value={report.issues.length.toString()}
                icon={<AlertTriangle className="w-6 h-6 text-warning" />}
              />
              <MetricCard
                label="AI 建议"
                value={(report.ai_suggestions?.length || 0).toString()}
                icon={<Lightbulb className="w-6 h-6 text-success" />}
              />
              <MetricCard
                label="评估时间"
                value={new Date(report.created_at).toLocaleDateString('zh-CN')}
                icon={<FileText className="w-6 h-6 text-info" />}
              />
            </div>
          </div>

          {/* URL Display */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <div className="flex items-center gap-3">
              <ExternalLink className="w-5 h-5 text-gray-400" />
              <a
                href={report.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 underline break-all"
              >
                {report.url}
              </a>
            </div>
          </div>
        </motion.div>

        {/* Radar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">维度分析</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar
                  name="得分"
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

          {/* Metric Details */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
            {Object.entries(report.metrics).map(([key, value], index) => (
              <div
                key={key}
                className="bg-gray-50 rounded-lg p-4"
              >
                <div className="text-sm text-gray-600 mb-2">{getMetricName(key)}</div>
                <div className="flex items-end justify-between">
                  <div className={`text-2xl font-bold ${getScoreColor(value.score)}`}>
                    {value.score}
                  </div>
                  <div className="text-sm text-gray-500">
                    / {value.maxScore}
                  </div>
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{
                      width: `${(value.score / value.maxScore) * 100}%`,
                      backgroundColor: COLORS[index % COLORS.length],
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Issues List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">问题清单</h2>
          {report.issues.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
              <p className="text-xl text-gray-600">太棒了！未发现明显问题</p>
            </div>
          ) : (
            <div className="space-y-4">
              {report.issues
                .sort((a, b) => {
                  const priorityOrder = { high: 0, medium: 1, low: 2 };
                  return priorityOrder[a.priority] - priorityOrder[b.priority];
                })
                .map((issue, index) => (
                  <div
                    key={issue.id || index}
                    className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`flex-shrink-0 p-2 rounded-lg ${getPriorityColor(issue.priority)}`}>
                        {getPriorityIcon(issue.priority)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {issue.title}
                          </h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(issue.priority)}`}>
                            {issue.priority === 'high' ? '严重' : issue.priority === 'medium' ? '中等' : '轻微'}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-3">{issue.description}</p>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 text-blue-800 font-medium mb-2">
                            <Lightbulb className="w-4 h-4" />
                            建议解决方案
                          </div>
                          <p className="text-blue-700 text-sm">{issue.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </motion.div>

        {/* AI Suggestions */}
        {report.ai_suggestions && report.ai_suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8"
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Lightbulb className="w-7 h-7 text-yellow-500" />
              AI 智能建议
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {report.ai_suggestions.map((suggestion, index) => (
                <div
                  key={suggestion.id || index}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start gap-3 mb-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                      <Lightbulb className="w-6 h-6 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {suggestion.title}
                      </h3>
                      <p className="text-sm text-gray-500">{suggestion.category}</p>
                    </div>
                  </div>
                  <p className="text-gray-600 mb-4">{suggestion.description}</p>
                  <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500">影响程度:</span>
                      <span className={`px-2 py-1 rounded ${
                        suggestion.estimatedImpact === 'high'
                          ? 'bg-green-100 text-green-800'
                          : suggestion.estimatedImpact === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {suggestion.estimatedImpact === 'high' ? '高' : suggestion.estimatedImpact === 'medium' ? '中' : '低'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500">实施难度:</span>
                      <span className={`px-2 py-1 rounded ${
                        suggestion.effort === 'high'
                          ? 'bg-red-100 text-red-800'
                          : suggestion.effort === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {suggestion.effort === 'high' ? '高' : suggestion.effort === 'medium' ? '中' : '低'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl shadow-lg p-8 text-white"
        >
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">准备好重新评估了吗？</h2>
            <p className="text-primary-100 mb-6 max-w-2xl mx-auto">
              根据报告建议优化网站后，可以重新进行评估以查看改进效果
            </p>
            <button
              onClick={() => router.push('/')}
              className="px-8 py-4 bg-white text-primary-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-flex items-center gap-2"
            >
              开始新的评估
              <ArrowLeft className="w-5 h-5 rotate-180" />
            </button>
          </div>
        </motion.div>
      </div>
    </main>
  );
}

function MetricCard({ label, value, icon }: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="text-center p-4 bg-gray-50 rounded-lg">
      <div className="flex justify-center mb-2">{icon}</div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
}

function getMetricName(key: string): string {
  const names: Record<string, string> = {
    content_quality: '内容质量',
    website_structure: '网站结构',
    user_experience: '用户体验',
    technical_compliance: '技术合规',
  };
  return names[key] || key;
}
