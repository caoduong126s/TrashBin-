"use client"

import { Check, Share2, RotateCcw, Lightbulb } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { ClassificationFeedback } from "@/components/classification-feedback"

export interface ClassificationResult {
  className: string
  classNameEn: string
  confidence: number
  binType: "recyclable" | "general" | "hazardous" | "organic"
  binName: string
  instruction: string
  tips: string[]
  topPredictions: { name: string; confidence: number }[]
}

interface ClassificationResultProps {
  result: ClassificationResult
  imagePreview: string
  onClassifyAgain: () => void
}

const binConfig = {
  recyclable: {
    color: "#3b82f6",
    bgColor: "#eff6ff",
    borderColor: "#3b82f6",
    icon: "♻️",
    label: "THÙNG TÁI CHẾ",
  },
  general: {
    color: "#6b7280",
    bgColor: "#f3f4f6",
    borderColor: "#6b7280",
    icon: "🗑️",
    label: "THÙNG RÁC THÔNG THƯỜNG",
  },
  hazardous: {
    color: "#ef4444",
    bgColor: "#fee2e2",
    borderColor: "#ef4444",
    icon: "⚠️",
    label: "THÙNG RÁC NGUY HẠI",
  },
  organic: {
    color: "#f59e0b",
    bgColor: "#fef3c7",
    borderColor: "#f59e0b",
    icon: "🍂",
    label: "THÙNG HỮU CƠ",
  },
}

export function ClassificationResultSection({ result, imagePreview, onClassifyAgain }: ClassificationResultProps) {
  const bin = binConfig[result.binType]

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 85) return "#10b981"
    if (confidence >= 70) return "#fcd34d"
    return "#f59e0b"
  }

  return (
    <section className="py-20 bg-white">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left Column - Main Result */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-[20px] shadow-xl overflow-hidden animate-fade-in-up">
              {/* Success Header */}
              <div className="h-[60px] bg-gradient-to-r from-[#10b981] to-[#059669] flex items-center justify-center gap-3">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <Check className="w-5 h-5 text-white" />
                </div>
                <span className="text-white font-semibold text-lg">Phân tích thành công</span>
              </div>

              <div className="p-8 space-y-8">
                {/* Image */}
                <div className="flex justify-center">
                  <img
                    src={imagePreview || "/placeholder.svg"}
                    alt="Classified item"
                    className="w-[300px] h-[300px] object-cover rounded-2xl shadow-md"
                  />
                </div>

                {/* Class Name */}
                <div className="text-center">
                  <h2 className="text-3xl font-bold text-[#111827] mb-1">{result.className}</h2>
                  <p className="text-[#6b7280]">{result.classNameEn}</p>
                </div>

                {/* Confidence */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-[#6b7280] font-medium">Độ tin cậy</span>
                    <span className="font-bold text-lg" style={{ color: getConfidenceColor(result.confidence) }}>
                      {result.confidence.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-3 bg-[#e5e7eb] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full animate-progress-fill"
                      style={{
                        width: `${result.confidence}%`,
                        backgroundColor: getConfidenceColor(result.confidence),
                      }}
                    />
                  </div>
                </div>

                {/* Bin Type */}
                <div
                  className="p-6 rounded-2xl border-2"
                  style={{
                    backgroundColor: bin.bgColor,
                    borderColor: bin.borderColor,
                  }}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-5xl">{bin.icon}</span>
                    <div>
                      <h3 className="font-bold text-lg" style={{ color: bin.color }}>
                        {bin.label}
                      </h3>
                      <p className="text-[#6b7280]">{result.instruction}</p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                  <Button
                    onClick={onClassifyAgain}
                    className="flex-1 bg-[#10b981] hover:bg-[#059669] text-white py-3 h-auto rounded-lg"
                  >
                    <RotateCcw className="w-5 h-5 mr-2" />
                    Phân loại tiếp
                  </Button>
                  <Button
                    variant="ghost"
                    className="px-4 py-3 h-auto rounded-lg hover:bg-[#f3f4f6]"
                    aria-label="Share result"
                  >
                    <Share2 className="w-5 h-5" />
                  </Button>
                </div>

                {/* Feedback Section */}
                <ClassificationFeedback
                  detectedClass={result.className}
                  detectedClassEn={result.classNameEn}
                />
              </div>
            </div>
          </div>

          {/* Right Column - Tips & Predictions */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tips Card */}
            <div
              className="bg-white rounded-2xl border border-[#e5e7eb] p-6 shadow-md animate-fade-in-up"
              style={{ animationDelay: "100ms" }}
            >
              <div className="flex items-center gap-3 mb-4">
                <Lightbulb className="w-6 h-6 text-[#f59e0b]" />
                <h3 className="font-bold text-lg text-[#111827]">Mẹo tái chế</h3>
              </div>
              <ul className="space-y-3">
                {result.tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-3 text-[#6b7280]">
                    <span className="text-lg">{index === 0 ? "🚿" : index === 1 ? "✂️" : "♻️"}</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Top Predictions Card */}
            <div
              className="bg-white rounded-2xl border border-[#e5e7eb] p-6 shadow-md animate-fade-in-up"
              style={{ animationDelay: "200ms" }}
            >
              <h3 className="font-bold text-lg text-[#111827] mb-4">Top 3 dự đoán</h3>
              <div className="space-y-4">
                {result.topPredictions.map((prediction, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-[#374151] font-medium">{prediction.name}</span>
                      <span className="text-[#6b7280]">{prediction.confidence}%</span>
                    </div>
                    <div className="h-2 bg-[#e5e7eb] rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all duration-500",
                          index === 0 ? "bg-[#10b981]" : "bg-[#9ca3af]",
                        )}
                        style={{ width: `${prediction.confidence}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
