'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User, AlertTriangle, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    // 验证密码
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      setIsLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('密码长度至少为 6 位');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
          full_name: fullName || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '注册失败');
      }

      const data = await response.json();

      setSuccess('注册成功！正在跳转到登录页面...');
      
      // 延迟跳转到登录页面
      setTimeout(() => {
        router.push('/login');
      }, 1500);

    } catch (err: any) {
      setError(err.message || '注册失败，请稍后重试');
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-4 py-12">
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

        {/* Register Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <div className="text-center mb-6">
            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <UserPlus className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">创建账户</h2>
            <p className="text-gray-600">注册以保存评估历史和导出报告</p>
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

            {/* Full Name Input (Optional) */}
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
                姓名（可选）
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="你的名字"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
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
                  placeholder="至少 6 位"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
                  required
                  minLength={6}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Confirm Password Input */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                确认密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="再次输入密码"
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
                  注册中...
                </>
              ) : (
                <>
                  <UserPlus className="w-5 h-5" />
                  注册
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center text-sm text-gray-600">
            已有账户？{' '}
            <Link href="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              立即登录
            </Link>
          </div>

          {/* Terms Notice */}
          <div className="mt-4 text-xs text-gray-500 text-center">
            注册即表示你同意我们的服务条款和隐私政策
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
