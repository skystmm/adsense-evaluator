'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, CheckCircle, AlertTriangle, Lightbulb, ArrowRight, Loader2, BarChart3, Clock, TrendingUp, LogOut, User } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { isAuthenticated, getUserEmail, logout, getAuthHeaders } from '@/lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const router = useRouter();
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [useAI, setUseAI] = useState(true);
  const [usePlaywright, setUsePlaywright] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    setIsLoggedIn(isAuthenticated());
    setUserEmail(getUserEmail());
  }, []);

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
    setUserEmail(null);
    router.refresh();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    
    // 验证 URL 格式
    try {
      new URL(url);
    } catch {
      setError('请输入有效的 URL（包含 http:// 或 https://）');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // 调用后端 API 进行评估
      const response = await fetch(`${API_BASE_URL}/api/evaluate/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          url: url,
          include_ai_analysis: useAI,
          use_playwright: usePlaywright,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '评估失败');
      }
      
      const data = await response.json();
      
      // 跳转到报告页面
      router.push(`/report/${data.report_id}`);
      
    } catch (err: any) {
      setError(err.message || '评估失败，请稍后重试');
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-8 h-8 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">AdSense 评估工具</h1>
          </div>
          <nav className="flex items-center gap-6">
            <a href="/history" className="text-gray-600 hover:text-gray-900 flex items-center gap-1">
              <Clock className="w-4 h-4" />
              历史记录
            </a>
            <a href="/stats" className="text-gray-600 hover:text-gray-900 flex items-center gap-1">
              <BarChart3 className="w-4 h-4" />
              统计
            </a>
            {isLoggedIn ? (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <User className="w-4 h-4" />
                  <span>{userEmail}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-gray-600 hover:text-gray-900 flex items-center gap-1 text-sm"
                >
                  <LogOut className="w-4 h-4" />
                  退出
                </button>
              </div>
            ) : (
              <div className="flex gap-4">
                <Link href="/login" className="text-gray-600 hover:text-gray-900 flex items-center gap-1 text-sm">
                  登录
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
                >
                  注册
                </Link>
              </div>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-4xl mx-auto px-4 py-20 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-bold text-gray-900 mb-6"
        >
          评估你的网站是否符合<br />
          <span className="text-primary-600">AdSense 要求</span>
        </motion.h2>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-xl text-gray-600 mb-10"
        >
          输入网站 URL，获取详细的 AdSense 接入可行性报告、问题诊断和 AI 整改建议
        </motion.p>

        {/* Input Form */}
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          onSubmit={handleSubmit}
          className="max-w-2xl mx-auto"
        >
          <div className="flex gap-3 mb-4">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="输入你的网站 URL（例如：https://example.com）"
              className="flex-1 px-6 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent text-lg"
              required
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-8 py-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  评估中...
                </>
              ) : (
                <>
                  开始评估
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-left"
              >
                <AlertTriangle className="w-5 h-5 inline mr-2" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Options */}
          <div className="flex gap-6 justify-center text-sm text-gray-600">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useAI}
                onChange={(e) => setUseAI(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                disabled={isLoading}
              />
              <span className="flex items-center gap-1">
                <Lightbulb className="w-4 h-4" />
                AI 分析建议
              </span>
            </label>
            
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={usePlaywright}
                onChange={(e) => setUsePlaywright(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                disabled={isLoading}
              />
              <span className="flex items-center gap-1">
                <Search className="w-4 h-4" />
                深度爬取（JavaScript 渲染）
              </span>
            </label>
          </div>
        </motion.form>
      </section>

      {/* Features Section */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Search className="w-8 h-8 text-primary-600" />}
            title="快速评估"
            description="输入 URL 后自动分析网站内容、结构和用户体验，30 秒内生成详细评估报告"
          />
          <FeatureCard
            icon={<AlertTriangle className="w-8 h-8 text-warning" />}
            title="问题诊断"
            description="根据 AdSense 官方标准识别具体问题，按优先级排序，让你知道先改什么"
          />
          <FeatureCard
            icon={<Lightbulb className="w-8 h-8 text-success" />}
            title="AI 建议"
            description="基于 AI 分析提供个性化整改建议，预估通过概率，帮助你高效优化网站"
          />
        </div>

        {/* Stats Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-20 grid md:grid-cols-3 gap-6"
        >
          <StatCard
            icon={<TrendingUp className="w-6 h-6 text-primary-600" />}
            label="已评估网站"
            value="100+"
            description="累计评估网站数量"
          />
          <StatCard
            icon={<CheckCircle className="w-6 h-6 text-success" />}
            label="平均通过率"
            value="68%"
            description="优化后通过 AdSense 审核"
          />
          <StatCard
            icon={<Clock className="w-6 h-6 text-info" />}
            label="平均优化时间"
            value="2-3 周"
            description="从评估到通过审核"
          />
        </motion.div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            工作原理
          </h3>
          <div className="grid md:grid-cols-4 gap-8">
            <StepCard
              number="1"
              title="输入 URL"
              description="提供要评估的网站地址"
            />
            <StepCard
              number="2"
              title="智能爬取"
              description="分析网站内容、结构和性能"
            />
            <StepCard
              number="3"
              title="AI 分析"
              description="生成详细评分和问题诊断"
            />
            <StepCard
              number="4"
              title="获取报告"
              description="查看完整评估结果和改进建议"
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50 mt-20">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-gray-600">
          <p>© 2026 AdSense 评估工具。本网站与 Google AdSense 无关。</p>
          <p className="text-sm mt-2">
            本工具提供评估建议，不保证 AdSense 审核通过
          </p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  );
}

function StatCard({ icon, label, value, description }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
      <div className="flex justify-center mb-3">{icon}</div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm font-medium text-gray-600 mb-1">{label}</div>
      <div className="text-xs text-gray-500">{description}</div>
    </div>
  );
}

function StepCard({ number, title, description }: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h4 className="text-lg font-semibold text-gray-900 mb-2">{title}</h4>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}
