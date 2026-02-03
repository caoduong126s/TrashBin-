"use client"

import { Upload, Camera, ImageIcon, Recycle, Leaf, Video } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface HeroSectionProps {
  onUploadClick: () => void
  onCameraClick: () => void
  onSampleClick: () => void
}

export function HeroSection({ onUploadClick, onCameraClick, onSampleClick }: HeroSectionProps) {
  return (
    <section className="relative bg-gradient-to-b from-[#ecfdf5] to-white dark:from-gray-900 dark:to-gray-800 py-24 md:py-32 overflow-hidden">
      {/* Floating decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-[10%] text-[#10b981]/20 animate-float" style={{ animationDelay: "0s" }}>
          <Leaf className="w-12 h-12" />
        </div>
        <div className="absolute top-40 right-[15%] text-[#10b981]/15 animate-float" style={{ animationDelay: "0.5s" }}>
          <Recycle className="w-16 h-16" />
        </div>
        <div className="absolute bottom-32 left-[20%] text-[#10b981]/10 animate-float" style={{ animationDelay: "1s" }}>
          <Leaf className="w-10 h-10" />
        </div>
        <div
          className="absolute bottom-20 right-[25%] text-[#3b82f6]/15 animate-float"
          style={{ animationDelay: "1.5s" }}
        >
          <Recycle className="w-8 h-8" />
        </div>
      </div>

      <div className="max-w-[1200px] mx-auto px-6 text-center relative z-10">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#111827] dark:text-white mb-6 text-balance">
          Phân loại rác thông minh với AI
        </h1>
        <p className="text-lg md:text-xl text-[#6b7280] dark:text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
          Upload ảnh → Nhận kết quả ngay lập tức → Biết cách tái chế đúng
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button
            onClick={onUploadClick}
            className="bg-[#10b981] hover:bg-[#059669] text-white px-6 py-3 h-auto text-base font-medium rounded-lg shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all"
          >
            <Upload className="w-5 h-5 mr-2" />
            Upload ảnh
          </Button>
          <Button
            onClick={onCameraClick}
            className="bg-[#3b82f6] hover:bg-[#2563eb] text-white px-6 py-3 h-auto text-base font-medium rounded-lg shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all"
          >
            <Camera className="w-5 h-5 mr-2" />
            Chụp ảnh
          </Button>

          {/* NEW: Real-time Detection Button */}
          <Link href="/realtime">
            <Button
              className="bg-gradient-to-r from-[#10b981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white px-6 py-3 h-auto text-base font-medium rounded-lg shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all relative"
            >
              <Video className="w-5 h-5 mr-2" />
              Real-time
              <span className="ml-2 text-xs bg-white/20 px-2 py-0.5 rounded-full font-semibold animate-pulse">
                MỚI
              </span>
            </Button>
          </Link>

          <Button
            onClick={onSampleClick}
            variant="outline"
            className="border-2 border-[#10b981] text-[#10b981] hover:bg-[#ecfdf5] dark:hover:bg-[#10b981]/20 px-6 py-3 h-auto text-base font-medium rounded-lg hover:scale-[1.02] active:scale-[0.98] transition-all bg-transparent"
          >
            <ImageIcon className="w-5 h-5 mr-2" />
            Xem mẫu
          </Button>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-4xl mx-auto">
          <div className="text-center p-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#10b981]/10 mb-3">
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="font-semibold text-[#111827] dark:text-white mb-1">
              Độ chính xác 98.97%
            </h3>
            <p className="text-sm text-[#6b7280] dark:text-gray-400">
              Sử dụng AI tiên tiến
            </p>
          </div>

          <div className="text-center p-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#3b82f6]/10 mb-3">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="font-semibold text-[#111827] dark:text-white mb-1">
              Phát hiện tức thì
            </h3>
            <p className="text-sm text-[#6b7280] dark:text-gray-400">
              Kết quả trong 1-2 giây
            </p>
          </div>

          <div className="text-center p-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#10b981]/10 mb-3">
              <span className="text-2xl">♻️</span>
            </div>
            <h3 className="font-semibold text-[#111827] dark:text-white mb-1">
              Thân thiện môi trường
            </h3>
            <p className="text-sm text-[#6b7280] dark:text-gray-400">
              Góp phần bảo vệ hành tinh
            </p>
          </div>
        </div>
      </div>

      {/* Wave decoration */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full">
          <path
            d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            className="fill-white dark:fill-gray-800"
          />
        </svg>
      </div>
    </section>
  )
}