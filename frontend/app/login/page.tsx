'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, Mail, Lock, AlertTriangle, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      // 使用 OAuth2 密码模式登录
      const formData = new URLSearchParams();
      formData.append('username', email); // OAuth2 使用 username 字段
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '登录失败');
      }

      const data = await response.json();

      // 保存 Token 到 localStorage
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_id', data.user_id.toString());
      localStorage.setItem('user_email', data.email);

      setSuccess('登录成功，正在跳转...');
      
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        router.push('/');
      }, 1000);

    } catch (err: any) {
      setError(err.message || '登录失败，请稍后重试');
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2">
            <CheckCircle className="w-10 h-10 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">AdSense 评估工具</h1>
          </Link>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="text-center mb-6">
            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <LogIn className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">欢迎回来</h2>
            <p className="text-gray-600">登录你的账户以继续</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                邮箱地址
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm flex items-center gap-2">
                <CheckCircle className="w-4 h-4 flex-shrink-0" />
                {success}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  登录中...
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  登录
                </>
              )}
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center text-sm text-gray-600">
            还没有账户？{' '}
            <Link href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              立即注册
            </Link>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-gray-600 hover:text-gray-900 text-sm">
            ← 返回首页
          </Link>
        </div>
      </motion.div>
    </main>
  );
}
