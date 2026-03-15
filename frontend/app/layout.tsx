import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AdSense 评估工具 - 检查你的网站是否符合 AdSense 要求',
  description: '免费评估你的网站是否符合 Google AdSense 接入要求，获取详细的问题诊断和整改建议',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
