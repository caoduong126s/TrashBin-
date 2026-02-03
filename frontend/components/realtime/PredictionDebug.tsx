'use client';

/**
 * PredictionDebug Component
 * Shows all class predictions for debugging
 */

import { motion, AnimatePresence } from 'framer-motion';
import { Bug, X } from 'lucide-react';
import { useState } from 'react';

interface PredictionDebugProps {
  predictions?: Record<string, number>;
  topClass?: string;
  usedSecondChoice?: boolean;
}

export const PredictionDebug = ({
  predictions,
  topClass,
  usedSecondChoice
}: PredictionDebugProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!predictions) return null;

  // Sort predictions by confidence
  const sortedPredictions = Object.entries(predictions)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5); // Top 5

  return (
    <>
      {/* Toggle button */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        onClick={() => setIsExpanded(!isExpanded)}
        className="fixed top-4 right-4 z-50 p-3 bg-gray-900 text-white rounded-full shadow-lg hover:bg-gray-800 transition-colors"
        title="Debug predictions"
      >
        <Bug className="w-5 h-5" />
      </motion.button>

      {/* Debug panel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="fixed top-16 right-4 z-50 w-80 bg-white rounded-lg shadow-2xl border border-gray-200 overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gray-900 text-white p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bug className="w-5 h-5" />
                <h3 className="font-bold">Debug: Predictions</h3>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Second choice warning */}
            {usedSecondChoice && (
              <div className="bg-yellow-50 border-b border-yellow-200 p-3">
                <p className="text-sm text-yellow-800 font-semibold">
                  ⚠️ Dùng lựa chọn thứ 2
                </p>
                <p className="text-xs text-yellow-700">
                  Lựa chọn đầu không đạt ngưỡng tin cậy
                </p>
              </div>
            )}

            {/* Predictions list */}
            <div className="p-4 space-y-3">
              {sortedPredictions.map(([className, confidence], index) => {
                const isTop = className === topClass;
                const percentage = confidence;

                return (
                  <motion.div
                    key={className}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`${
                      isTop ? 'bg-green-50 border-green-500' : 'bg-gray-50 border-gray-200'
                    } border-2 rounded-lg p-3`}
                  >
                    {/* Class info */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold ${
                          isTop ? 'text-green-700' : 'text-gray-500'
                        }`}>
                          #{index + 1}
                        </span>
                        <span className={`font-semibold ${
                          isTop ? 'text-green-900' : 'text-gray-700'
                        }`}>
                          {className}
                        </span>
                        {isTop && (
                          <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">
                            TOP
                          </span>
                        )}
                      </div>
                      <span className={`font-bold ${
                        isTop ? 'text-green-700' : 'text-gray-600'
                      }`}>
                        {percentage.toFixed(1)}%
                      </span>
                    </div>

                    {/* Progress bar */}
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 0.5, delay: index * 0.05 }}
                        className={`h-full ${
                          isTop
                            ? 'bg-gradient-to-r from-green-500 to-emerald-600'
                            : 'bg-gray-400'
                        }`}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Footer info */}
            <div className="bg-gray-50 border-t border-gray-200 p-3">
              <p className="text-xs text-gray-600">
                💡 Ngưỡng tin cậy: Pin 85%, Metal 75%, Other 65%
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
