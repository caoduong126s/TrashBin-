'use client';

/**
 * HazardWarning Component
 * Prominent warning for hazardous waste detection
 */

import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X, Info } from 'lucide-react';
import { useEffect, useState } from 'react';

interface HazardWarningProps {
  className: string;
  confidence: number;
  onDismiss?: () => void;
  autoHide?: boolean;
  autoHideDelay?: number;
}

export const HazardWarning = ({
  className,
  confidence,
  onDismiss,
  autoHide = false,
  autoHideDelay = 5000
}: HazardWarningProps) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (autoHide) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onDismiss?.();
      }, autoHideDelay);

      return () => clearTimeout(timer);
    }
  }, [autoHide, autoHideDelay, onDismiss]);

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  const hazardInfo: Record<string, { title: string; warnings: string[]; icon: string }> = {
    'Pin': {
      title: 'RÁC NGUY HẠI',
      icon: '🔋',
      warnings: [
        'Pin chứa hóa chất độc hại',
        'KHÔNG vứt vào thùng rác thường',
        'Có thể gây ô nhiễm môi trường nghiêm trọng',
        'Pin Lithium có nguy cơ cháy nổ'
      ]
    }
  };

  const info = hazardInfo[className];
  if (!info) return null;

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={handleDismiss}
          />

          {/* Warning Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-full md:max-w-md z-50"
          >
            <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border-4 border-red-500 animate-pulse-border">
              {/* Flashing header */}
              <motion.div
                animate={{
                  backgroundColor: ['#ef4444', '#dc2626', '#ef4444']
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
                className="p-6 text-white"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <motion.div
                      animate={{
                        rotate: [0, -10, 10, -10, 0],
                        scale: [1, 1.1, 1]
                      }}
                      transition={{
                        duration: 0.5,
                        repeat: Infinity,
                        repeatDelay: 1
                      }}
                    >
                      <AlertTriangle className="w-8 h-8" />
                    </motion.div>
                    <div>
                      <h2 className="text-2xl font-bold">{info.title}</h2>
                      <p className="text-sm opacity-90">
                        Phát hiện: {className}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleDismiss}
                    className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {/* Confidence */}
                <div className="bg-white/20 rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span>Độ chính xác</span>
                    <span className="font-bold">{confidence.toFixed(1)}%</span>
                  </div>
                  <div className="h-2 bg-white/30 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${confidence}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                      className="h-full bg-white rounded-full"
                    />
                  </div>
                </div>
              </motion.div>

              {/* Warnings */}
              <div className="p-6 space-y-4">
                <div className="flex items-start gap-3">
                  <span className="text-4xl">{info.icon}</span>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 mb-2">
                      Cảnh báo quan trọng:
                    </h3>
                    <ul className="space-y-2">
                      {info.warnings.map((warning, index) => (
                        <motion.li
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-start gap-2 text-sm text-gray-700"
                        >
                          <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <span>{warning}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Action box */}
                <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <Info className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-red-900 mb-1">
                        Hành động cần làm:
                      </p>
                      <p className="text-sm text-red-800">
                        Đem đến điểm thu gom rác nguy hại hoặc cửa hàng điện tử gần nhất.
                        <strong> KHÔNG</strong> vứt vào thùng rác thường!
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="p-6 pt-0 flex gap-3">
                <button
                  onClick={handleDismiss}
                  className="flex-1 py-3 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Đã hiểu
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// CSS for pulsing border animation
// Add to global CSS:
/*
@keyframes pulse-border {
  0%, 100% { border-color: rgb(239 68 68); }
  50% { border-color: rgb(220 38 38); }
}

.animate-pulse-border {
  animation: pulse-border 1s ease-in-out infinite;
}
*/
