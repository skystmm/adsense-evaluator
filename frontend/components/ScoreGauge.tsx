'use client';

import { motion } from 'framer-motion';

interface ScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export default function ScoreGauge({ score, size = 'md', showLabel = true }: ScoreGaugeProps) {
  const sizeClasses = {
    sm: 'w-20 h-20 text-xl',
    md: 'w-32 h-32 text-3xl',
    lg: 'w-40 h-40 text-5xl',
  };

  const percentage = Math.min(100, Math.max(0, score));
  const circumference = 2 * Math.PI * 45; // r=45
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getColor = (score: number) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  const color = getColor(score);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`${sizeClasses[size]} relative`}
    >
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="8"
        />
        {/* Progress circle */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-bold" style={{ color }}>
          {score}
        </span>
      </div>
      {showLabel && size !== 'sm' && (
        <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-sm text-gray-600 whitespace-nowrap">
          综合评分
        </div>
      )}
    </motion.div>
  );
}
