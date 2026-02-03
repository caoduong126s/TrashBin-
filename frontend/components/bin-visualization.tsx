"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

interface BinData {
  id: "recyclable" | "general" | "hazardous" | "organic"
  icon: string
  label: string
  labelVi: string
  count: number
  examples: string
  color: string
  bgColor: string
}

interface BinVisualizationProps {
  activeBin?: "recyclable" | "general" | "hazardous" | "organic" | null
}

const bins: BinData[] = [
  {
    id: "recyclable",
    icon: "♻️",
    label: "Recyclable",
    labelVi: "Tái chế",
    count: 13,
    examples: "Ví dụ: Nhựa, Giấy, Kim loại",
    color: "#3b82f6",
    bgColor: "#eff6ff",
  },
  {
    id: "organic",
    icon: "🍂",
    label: "Organic",
    labelVi: "Hữu cơ",
    count: 8,
    examples: "Ví dụ: Thực phẩm thừa, Lá cây",
    color: "#f59e0b",
    bgColor: "#fef3c7",
  },
  {
    id: "general",
    icon: "🗑️",
    label: "General",
    labelVi: "Thông thường",
    count: 24,
    examples: "Ví dụ: Rác ăn, Vải vụn",
    color: "#6b7280",
    bgColor: "#f3f4f6",
  },
  {
    id: "hazardous",
    icon: "⚠️",
    label: "Hazardous",
    labelVi: "Nguy hại",
    count: 3,
    examples: "Ví dụ: Pin, Thuốc, Hóa chất",
    color: "#ef4444",
    bgColor: "#fee2e2",
  },
]

export function BinVisualization({ activeBin }: BinVisualizationProps) {
  const [animatingBin, setAnimatingBin] = useState<string | null>(null)

  useEffect(() => {
    if (activeBin) {
      setAnimatingBin(activeBin)
      const timer = setTimeout(() => setAnimatingBin(null), 1000)
      return () => clearTimeout(timer)
    }
  }, [activeBin])

  return (
    <section className="py-24 bg-gradient-to-b from-[#f9fafb] to-white">
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-[#111827] mb-16">Hệ thống thùng rác hiện tại</h2>

        <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12">
          {bins.map((bin) => (
            <div key={bin.id} className="flex flex-col items-center">
              {/* Bin Container */}
              <div
                className={cn(
                  "relative w-[180px] h-[240px] rounded-t-2xl rounded-b-3xl transition-all duration-300 cursor-pointer",
                  animatingBin === bin.id && "animate-bin-jump",
                )}
                style={{
                  backgroundColor: bin.bgColor,
                  boxShadow: animatingBin === bin.id ? `0 0 30px ${bin.color}50` : "0 10px 30px rgba(0,0,0,0.1)",
                }}
              >
                {/* Lid */}
                <div
                  className="absolute top-0 left-0 right-0 h-4 rounded-t-2xl"
                  style={{ backgroundColor: bin.color, opacity: 0.3 }}
                />

                {/* Icon */}
                <div className="absolute top-8 left-1/2 -translate-x-1/2">
                  <div
                    className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-md"
                    style={{
                      boxShadow: animatingBin === bin.id ? `0 0 20px ${bin.color}50` : "0 4px 12px rgba(0,0,0,0.1)",
                    }}
                  >
                    <span className="text-3xl">{bin.icon}</span>
                  </div>
                </div>

                {/* Fill Level */}
                <div
                  className="absolute bottom-0 left-0 right-0 rounded-b-3xl transition-all duration-500"
                  style={{
                    height: `${Math.min(bin.count * 3, 70)}%`,
                    backgroundColor: bin.color,
                    opacity: 0.2,
                  }}
                />

                {/* Ring glow when active */}
                {animatingBin === bin.id && (
                  <div
                    className="absolute inset-0 rounded-t-2xl rounded-b-3xl border-4 animate-pulse"
                    style={{ borderColor: bin.color }}
                  />
                )}
              </div>

              {/* Label */}
              <div className="mt-6 text-center">
                <h3 className="font-bold text-xl text-[#111827]">{bin.labelVi}</h3>
                {/* <p className="text-sm font-semibold uppercase tracking-wider text-[#6b7280] mt-1">{bin.count} ITEMS</p> */}
                <p className="text-sm text-[#9ca3af] mt-2">{bin.examples}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
