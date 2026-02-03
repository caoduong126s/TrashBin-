'use client';

/**
 * DetectionFeedback Component
 * Shows detection results as overlay on camera view
 */

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, TrendingUp } from 'lucide-react';
import type { DetectionResult } from '@/hooks/useWebSocketDetection';

interface DetectionFeedbackProps {
  result: DetectionResult | null;
  fps: number;
  isProcessing: boolean;
}

const BIN_COLORS = {
  recyclable: 'bg-green-500',
  hazardous: 'bg-red-500',
  general: 'bg-gray-500', // Guide says Gray
  organic: 'bg-orange-500',
};

const BIN_LABELS = {
  recyclable: 'Tái chế',
  hazardous: 'Nguy hại',
  general: 'Thông thường',
  organic: 'Hữu cơ',
};

export const DetectionFeedback = ({
  result,
  fps,
  isProcessing,
}: DetectionFeedbackProps) => {
  if (!result || !result.success) {
    return (
      <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm rounded-lg p-3">
        <div className="flex items-center gap-2 text-white">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Đang kết nối...</span>
        </div>
      </div>
    );
  }

  // extract primary detection
  const detection = result.data?.detections?.[0];
  const stable = result.data?.stable;
  const preprocessing = result.data?.preprocessing;
  const metadata = result.metadata;
  // Optional fields not in guide but used in UI (legacy or enhanced)
  const message = (result.data as any)?.message;
  const progress = (result.data as any)?.progress;

  if (!detection) return null;

  const {
    class_name,
    confidence,
    bin_type,
  } = detection;

  const binColor = BIN_COLORS[bin_type] || BIN_COLORS.general;
  const binLabel = BIN_LABELS[bin_type] || 'Không xác định';

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Top left: Status & Progress */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm rounded-lg p-3 space-y-2"
      >
        {/* Status */}
        <div className="flex items-center gap-2">
          {stable ? (
            <>
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <span className="text-white font-semibold">Ổn định</span>
            </>
          ) : (
            <>
              <Loader2 className="w-5 h-5 text-yellow-500 animate-spin" />
              <span className="text-white text-sm">{message || 'Đang phân tích...'}</span>
            </>
          )}
        </div>

        {/* Progress bar */}
        {progress && !stable && (
          <div className="w-48">
            <div className="flex justify-between text-xs text-white/70 mb-1">
              <span>Tiến trình</span>
              <span>{progress[0]}/{progress[1]}</span>
            </div>
            <div className="h-1 bg-white/20 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(progress[0] / progress[1]) * 100}%` }}
                className="h-full bg-yellow-500"
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        )}
      </motion.div>

      {/* Low Light Indicator */}
      {preprocessing?.enhancement_applied && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="absolute top-20 left-4 bg-purple-900/80 backdrop-blur-sm rounded-lg p-2 border border-purple-500/50"
        >
          <div className="flex items-center gap-2 text-purple-200">
            <div className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
            <span className="text-xs font-medium">Low Light Mode</span>
          </div>
        </motion.div>
      )}

      {/* Bottom: Detection Result */}
      <AnimatePresence mode="wait">
        {confidence > 20 && (
          <motion.div
            key={class_name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-4 left-4 right-4"
          >
            <div className="bg-black/80 backdrop-blur-md rounded-lg p-4 border-2 border-white/20">
              {/* Main result */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex-1">
                  <motion.h3
                    initial={{ scale: 0.9 }}
                    animate={{ scale: stable ? 1.05 : 1 }}
                    transition={{ duration: 0.2 }}
                    className="text-2xl font-bold text-white mb-1"
                  >
                    {class_name}
                  </motion.h3>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${binColor}`} />
                    <span className="text-white/80 text-sm">{binLabel}</span>
                  </div>
                </div>

                {/* Confidence gauge */}
                <div className="relative w-20 h-20">
                  <svg className="w-full h-full -rotate-90">
                    {/* Background circle */}
                    <circle
                      cx="40"
                      cy="40"
                      r="32"
                      stroke="rgba(255,255,255,0.1)"
                      strokeWidth="6"
                      fill="none"
                    />
                    {/* Progress circle */}
                    <motion.circle
                      cx="40"
                      cy="40"
                      r="32"
                      stroke={stable ? '#10b981' : '#fbbf24'}
                      strokeWidth="6"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 32}`}
                      initial={{ strokeDashoffset: 2 * Math.PI * 32 }}
                      animate={{
                        strokeDashoffset:
                          2 * Math.PI * 32 * (1 - confidence / 100),
                      }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                      strokeLinecap="round"
                    />
                  </svg>
                  {/* Percentage text */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-white font-bold text-lg">
                      {confidence.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Metadata */}
              {metadata && (
                <div className="flex items-center justify-between text-xs text-white/60 pt-3 border-t border-white/10">
                  <span>FPS: {metadata.fps.toFixed(1)}</span>
                  <span>Xử lý: {metadata.processing_time_ms.toFixed(0)}ms</span>
                  <span>Frames: {metadata.frame_count}</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top right: FPS counter */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="absolute top-4 right-4 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-2"
      >
        <div className="flex items-center gap-2 text-white text-sm">
          <TrendingUp className="w-4 h-4" />
          <span>{fps.toFixed(1)} FPS</span>
        </div>
      </motion.div>
    </div>
  );
};
