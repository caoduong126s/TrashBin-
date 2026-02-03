'use client';

/**
 * DisposalInstructions Component
 * Shows step-by-step disposal instructions with animations
 */

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';
import { getDisposalInstructions, getHazardLevel } from '@/lib/disposalInstructions';
import { useState } from 'react';

interface DisposalInstructionsProps {
  className: string;
  binType: 'recyclable' | 'hazardous' | 'general' | 'organic';
  confidence: number;
  onClose?: () => void;
  onReportError?: () => void;
}

export const DisposalInstructions = ({
  className,
  binType,
  confidence,
  onClose,
  onReportError
}: DisposalInstructionsProps) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const instructions = getDisposalInstructions(className);
  // Default to medium hazard if new type not fully handled by helper yet, or ensure helper is updated.
  const hazardLevel = getHazardLevel(binType);

  if (!instructions) return null;

  const binColors = {
    recyclable: 'from-green-500 to-emerald-600',
    hazardous: 'from-red-500 to-rose-600',
    general: 'from-gray-500 to-slate-600',
    organic: 'from-orange-500 to-amber-600'
  };

  const hazardColors = {
    high: 'border-red-500 bg-red-50',
    medium: 'border-orange-500 bg-orange-50',
    low: 'border-green-500 bg-green-50'
  };

  return (
    <AnimatePresence>
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ duration: 0.3 }}
          className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50"
        >
          <div className={`bg-white rounded-2xl shadow-2xl border-2 ${hazardColors[hazardLevel]} overflow-hidden`}>
            {/* Header */}
            <div className={`bg-gradient-to-r ${binColors[binType]} p-4 text-white`}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-bold">{className}</h3>
                  <p className="text-sm opacity-90">
                    Độ chính xác: {confidence.toFixed(1)}%
                  </p>
                </div>
                {onClose && (
                  <button
                    onClick={onClose}
                    className="ml-4 p-2 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Warnings (if hazardous) */}
            {instructions.warnings && instructions.warnings.length > 0 && (
              <motion.div
                initial={{ height: 0 }}
                animate={{ height: 'auto' }}
                className="bg-red-500 text-white"
              >
                <div className="p-3 space-y-1">
                  {instructions.warnings.map((warning, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <p className="text-sm font-semibold">{warning}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Steps */}
            <div className="p-4">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                Cách xử lý:
              </h4>

              <div className="space-y-3">
                {instructions.steps.map((step, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <span className="text-2xl flex-shrink-0">{step.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold text-gray-500">
                          Bước {index + 1}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 font-medium">
                        {step.text}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Tips */}
            {instructions.tips && instructions.tips.length > 0 && (
              <div className="px-4 pb-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4 text-blue-600" />
                  Mẹo hay:
                </h4>
                <div className="space-y-2">
                  {instructions.tips.map((tip, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: instructions.steps.length * 0.1 + index * 0.1 }}
                      className="flex items-start gap-2 text-sm text-gray-600"
                    >
                      <span className="text-blue-500 mt-0.5">💡</span>
                      <p>{tip}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="px-4 pb-4 flex gap-2">
              <button
                onClick={() => setIsExpanded(false)}
                className="flex-1 py-2 px-4 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition-colors"
              >
                Thu gọn
              </button>
              {onReportError && (
                <button
                  onClick={onReportError}
                  className="flex-1 py-2 px-4 bg-orange-50 hover:bg-orange-100 border border-orange-200 rounded-lg text-sm font-medium text-orange-700 transition-colors flex items-center justify-center gap-1"
                >
                  <AlertTriangle className="w-4 h-4" />
                  Báo lỗi
                </button>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Collapsed state */}
      {!isExpanded && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          onClick={() => setIsExpanded(true)}
          className={`fixed bottom-4 right-4 p-4 bg-gradient-to-r ${binColors[binType]} text-white rounded-full shadow-lg hover:shadow-xl transition-shadow z-50`}
        >
          <Info className="w-6 h-6" />
        </motion.button>
      )}
    </AnimatePresence>
  );
};
