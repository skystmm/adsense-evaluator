'use client';

import { Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';

interface SuggestionCardProps {
  id: string;
  category: string;
  title: string;
  description: string;
  estimatedImpact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
  index?: number;
}

export default function SuggestionCard({
  id,
  category,
  title,
  description,
  estimatedImpact,
  effort,
  index = 0,
}: SuggestionCardProps) {
  const impactConfig = {
    high: { bg: 'bg-green-100', text: 'text-green-800', label: '高' },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '中' },
    low: { bg: 'bg-gray-100', text: 'text-gray-800', label: '低' },
  };

  const effortConfig = {
    high: { bg: 'bg-red-100', text: 'text-red-800', label: '高' },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '中' },
    low: { bg: 'bg-green-100', text: 'text-green-800', label: '低' },
  };

  const impact = impactConfig[estimatedImpact];
  const effortLabel = effortConfig[effort];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start gap-3 mb-4">
        <div className="flex-shrink-0 w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
          <Lightbulb className="w-6 h-6 text-yellow-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
          <p className="text-sm text-gray-500">{category}</p>
        </div>
      </div>
      <p className="text-gray-600 mb-4">{description}</p>
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-gray-500">影响程度:</span>
          <span className={`px-2 py-1 rounded ${impact.bg} ${impact.text}`}>
            {impact.label}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500">实施难度:</span>
          <span className={`px-2 py-1 rounded ${effortLabel.bg} ${effortLabel.text}`}>
            {effortLabel.label}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
