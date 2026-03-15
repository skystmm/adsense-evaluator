'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Filter,
  Calendar,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Trash2,
  ExternalLink,
  Loader2,
  X,
} from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface HistoryItem {
  report_id: string;
  url: string;
  overall_score: number;
  pass_probability: number;
  rating: string;
  created_at: string;
  issues_count: number;
  high_priority_issues: number;
}

interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  has_more: boolean;
}

export default function HistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState<HistoryResponse>({ items: [], total: 0, has_more: false });
  const [loading, setLoading] = useState(true);
  const [searchUrl, setSearchUrl] = useState('');
  const [filterDays, setFilterDays] = useState(30);
  const [filterMinScore, setFilterMinScore] = useState<number | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const pageSize = 20;

  useEffect(() => {
    fetchHistory();
  }, [currentPage, filterDays, filterMinScore]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const offset = (currentPage - 1) * pageSize;
      const params = new URLSearchParams({
        limit: pageSize.toString(),
        offset: offset.toString(),
        days: filterDays.toString(),
      });
      if (filterMinScore !== null) {
        params.append('min_score', filterMinScore.toString());
      }

      const response = await fetch(`${API_BASE_URL}/api/history/?${params}`);
      if (!response.ok) {
        throw new Error('加载历史记录失败');
      }
      const data = await response.json();
      setHistory(data);
    } catch (err: any) {
      console.error('加载历史记录失败:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (reportId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('确定要删除这条历史记录吗？')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/${reportId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        // 重新加载列表
        fetchHistory();
      } else {
        alert('删除失败，请稍后重试');
      }
    } catch (err) {
      alert('删除失败，请稍后重试');
    }
  };

  const handleApplyFilters = () => {
    setCurrentPage(1);
    fetchHistory();
    setShowFilters(false);
  };

  const handleClearFilters = () => {
    setSearchUrl('');
    setFilterDays(30);
    setFilterMinScore(null);
    setCurrentPage(1);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getRatingText = (score: number) => {
    if (score >= 90) return '优秀';
    if (score >= 75) return '良好';
    if (score >= 60) return '中等';
    if (score >= 40) return '较差';
    return '很差';
  };

  const filteredItems = searchUrl
    ? history.items.filter(item => item.url.toLowerCase().includes(searchUrl.toLowerCase()))
    : history.items;

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
              <h1 className="text-2xl font-bold text-gray-900">评估历史</h1>
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Filter className="w-4 h-4" />
              筛选
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchUrl}
              onChange={(e) => setSearchUrl(e.target.value)}
              placeholder="搜索网站 URL..."
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
            />
            {searchUrl && (
              <button
                onClick={() => setSearchUrl('')}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        {/* Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 bg-white border border-gray-200 rounded-lg p-6 overflow-hidden"
            >
              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    时间范围
                  </label>
                  <select
                    value={filterDays}
                    onChange={(e) => setFilterDays(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
                  >
                    <option value={7}>最近 7 天</option>
                    <option value={30}>最近 30 天</option>
                    <option value={90}>最近 90 天</option>
                    <option value={365}>最近 1 年</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    最低分数
                  </label>
                  <select
                    value={filterMinScore || ''}
                    onChange={(e) => setFilterMinScore(e.target.value ? Number(e.target.value) : null)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
                  >
                    <option value="">不限</option>
                    <option value={40}>40 分以上</option>
                    <option value={60}>60 分以上</option>
                    <option value={75}>75 分以上</option>
                    <option value={90}>90 分以上</option>
                  </select>
                </div>

                <div className="flex items-end gap-3">
                  <button
                    onClick={handleApplyFilters}
                    className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    应用筛选
                  </button>
                  <button
                    onClick={handleClearFilters}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    清除
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats Summary */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <StatCard
            icon={<Calendar className="w-6 h-6 text-primary-600" />}
            label="总评估数"
            value={history.total.toString()}
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6 text-success" />}
            label="平均通过率"
            value={history.items.length > 0
              ? `${Math.round(history.items.reduce((sum, item) => sum + item.pass_probability, 0) / history.items.length)}%`
              : '0%'
            }
          />
          <StatCard
            icon={<AlertTriangle className="w-6 h-6 text-warning" />}
            label="平均问题数"
            value={history.items.length > 0
              ? Math.round(history.items.reduce((sum, item) => sum + item.issues_count, 0) / history.items.length).toString()
              : '0'
            }
          />
        </div>

        {/* History List */}
        {loading ? (
          <div className="text-center py-12">
            <Loader2 className="w-12 h-12 animate-spin mx-auto text-primary-600 mb-4" />
            <p className="text-gray-600">加载历史记录...</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-gray-200">
            <Search className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">暂无历史记录</h3>
            <p className="text-gray-600 mb-6">开始第一次评估来创建历史记录</p>
            <a
              href="/"
              className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              开始评估
            </a>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
              <div className="divide-y divide-gray-200">
                {filteredItems.map((item) => (
                  <motion.div
                    key={item.report_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => router.push(`/report/${item.report_id}`)}
                  >
                    <div className="flex items-center gap-6">
                      {/* Score */}
                      <div className={`flex-shrink-0 w-16 h-16 rounded-full ${getScoreColor(item.overall_score)} flex items-center justify-center`}>
                        <span className="text-2xl font-bold">{item.overall_score}</span>
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 truncate">
                            {item.url}
                          </h3>
                          <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {new Date(item.created_at).toLocaleDateString('zh-CN')}
                          </span>
                          <span className="flex items-center gap-1">
                            <CheckCircle className="w-4 h-4" />
                            通过概率：{Math.round(item.pass_probability)}%
                          </span>
                          <span className="flex items-center gap-1">
                            <AlertTriangle className="w-4 h-4" />
                            {item.issues_count} 个问题
                            {item.high_priority_issues > 0 && (
                              <span className="text-red-600 font-medium">
                                ({item.high_priority_issues} 严重)
                              </span>
                            )}
                          </span>
                        </div>
                      </div>

                      {/* Rating Badge */}
                      <div className="flex-shrink-0 text-right">
                        <div className={`inline-block px-4 py-2 rounded-lg font-medium ${getScoreColor(item.overall_score)}`}>
                          {getRatingText(item.overall_score)}
                        </div>
                        <button
                          onClick={(e) => handleDelete(item.report_id, e)}
                          className="ml-3 p-2 text-gray-400 hover:text-red-600 transition-colors"
                          title="删除记录"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Pagination */}
            {history.has_more && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                  上一页
                </button>
                <span className="text-gray-600">
                  第 {currentPage} 页
                </span>
                <button
                  onClick={() => setCurrentPage(p => p + 1)}
                  disabled={!history.has_more}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
                >
                  下一页
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}

function StatCard({ icon, label, value }: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <span className="text-sm font-medium text-gray-600">{label}</span>
      </div>
      <div className="text-3xl font-bold text-gray-900">{value}</div>
    </div>
  );
}
