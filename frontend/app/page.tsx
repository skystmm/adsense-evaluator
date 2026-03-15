'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, CheckCircle, AlertTriangle, Lightbulb, ArrowRight } from 'lucide-react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    
    setIsLoading(true);
    // TODO: 调用后端 API 进行评估
    console.log('评估 URL:', url);
    // 实际实现时会跳转到报告页面
    setIsLoading(false);
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
          <nav className="flex gap-6">
            <a href="/history" className="text-gray-600 hover:text-gray-900">历史记录</a>
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
          <div className="flex gap-3">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="输入你的网站 URL（例如：https://example.com）"
              className="flex-1 px-6 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent text-lg"
              required
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-8 py-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? '评估中...' : (
                <>
                  开始评估
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
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
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50 mt-20">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-gray-600">
          <p>© 2026 AdSense 评估工具。本网站与 Google AdSense 无关。</p>
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
