'use client';

import { AlertCircle, AlertTriangle, Info, Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';

interface IssueCardProps {
  id: string;
  category: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  recommendation: string;
  index?: number;
}

export default function IssueCard({
  id,
  category,
  title,
  description,
  priority,
  recommendation,
  index = 0,
}: IssueCardProps) {
  const priorityConfig = {
    high: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-200',
      icon: AlertCircle,
      label: '严重',
    },
    medium: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      border: 'border-yellow-200',
      icon: AlertTriangle,
      label: '中等',
    },
    low: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-200',
      icon: Info,
      label: '轻微',
    },
  };

  const config = priorityConfig[priority];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start gap-4">
        <div className={`flex-shrink-0 p-2 rounded-lg ${config.bg} ${config.text}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text} ${config.border} border`}>
              {config.label}
            </span>
          </div>
          <p className="text-gray-600 mb-3">{description}</p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-blue-800 font-medium mb-2">
              <Lightbulb className="w-4 h-4" />
              建议解决方案
            </div>
            <p className="text-blue-700 text-sm">{recommendation}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
