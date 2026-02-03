"use client"

import type React from "react"

import { useState } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ChevronDown, Recycle, Trash2, AlertTriangle, Home } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface WasteCategory {
  id: string
  icon: React.ReactNode
  title: string
  titleEn: string
  color: string
  bgColor: string
  borderColor: string
  items: {
    name: string
    examples: string
    tips: string
  }[]
}

const wasteCategories: WasteCategory[] = [
  {
    id: "recyclable",
    icon: <Recycle className="w-6 h-6" />,
    title: "Rác tái chế",
    titleEn: "Recyclable Waste",
    color: "#3b82f6",
    bgColor: "#eff6ff",
    borderColor: "#3b82f6",
    items: [
      {
        name: "Nhựa",
        examples: "Chai nước, hộp đựng thức ăn, túi nhựa, nắp chai",
        tips: "Rửa sạch, tháo nắp, ép dẹp để tiết kiệm không gian",
      },
      {
        name: "Giấy & Carton",
        examples: "Báo cũ, thùng carton, hộp giấy, sách vở cũ",
        tips: "Giữ khô ráo, gấp phẳng, tách bỏ phần nhựa hoặc kim loại",
      },
      {
        name: "Kim loại",
        examples: "Lon nước ngọt, hộp thiếc, nắp kim loại",
        tips: "Rửa sạch, ép dẹp lon nhôm, tách riêng các loại kim loại",
      },
      {
        name: "Thủy tinh",
        examples: "Chai rượu, lọ thủy tinh, bình hoa vỡ",
        tips: "Rửa sạch, bọc cẩn thận nếu vỡ, phân loại theo màu",
      },
    ],
  },
  {
    id: "general",
    icon: <Trash2 className="w-6 h-6" />,
    title: "Rác thông thường",
    titleEn: "General Waste",
    color: "#6b7280",
    bgColor: "#f3f4f6",
    borderColor: "#6b7280",
    items: [
      {
        name: "Rác hữu cơ",
        examples: "Thức ăn thừa, vỏ trái cây, rau củ hỏng",
        tips: "Có thể ủ phân compost hoặc bỏ vào thùng rác thông thường",
      },
      {
        name: "Vải & Quần áo",
        examples: "Quần áo cũ rách, vải vụn, khăn cũ",
        tips: "Nếu còn tốt có thể quyên góp, nếu hỏng bỏ vào rác thông thường",
      },
      {
        name: "Đồ nhựa không tái chế",
        examples: "Túi nilon bẩn, hộp xốp, ống hút nhựa",
        tips: "Giảm thiểu sử dụng, bỏ vào thùng rác thông thường",
      },
      {
        name: "Sản phẩm vệ sinh",
        examples: "Tã, băng vệ sinh, khăn giấy đã sử dụng",
        tips: "Gói kín trước khi bỏ vào thùng rác",
      },
    ],
  },
  {
    id: "hazardous",
    icon: <AlertTriangle className="w-6 h-6" />,
    title: "Rác nguy hại",
    titleEn: "Hazardous Waste",
    color: "#ef4444",
    bgColor: "#fee2e2",
    borderColor: "#ef4444",
    items: [
      {
        name: "Pin & Ắc quy",
        examples: "Pin AA, AAA, pin điện thoại, ắc quy xe máy",
        tips: "KHÔNG bỏ chung với rác thường, mang đến điểm thu gom đặc biệt",
      },
      {
        name: "Thuốc & Dược phẩm",
        examples: "Thuốc hết hạn, ống tiêm, bông băng y tế",
        tips: "Mang đến nhà thuốc hoặc cơ sở y tế để xử lý đúng cách",
      },
      {
        name: "Hóa chất",
        examples: "Sơn, thuốc trừ sâu, chất tẩy rửa mạnh",
        tips: "Giữ nguyên bao bì, mang đến điểm thu gom chất thải nguy hại",
      },
      {
        name: "Thiết bị điện tử",
        examples: "Điện thoại cũ, máy tính hỏng, bóng đèn huỳnh quang",
        tips: "Mang đến điểm thu gom rác thải điện tử, có thể được tái chế một phần",
      },
    ],
  },
]

export default function GuidePage() {
  const [expandedCategory, setExpandedCategory] = useState<string | null>("recyclable")

  const toggleCategory = (categoryId: string) => {
    setExpandedCategory(expandedCategory === categoryId ? null : categoryId)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 px-6">
        <div className="max-w-[1200px] mx-auto py-8">
          <Link href="/">
            <Button variant="ghost" className="text-green-700 hover:text-green-800 hover:bg-green-50 font-bold gap-2 p-0">
              <Home className="w-5 h-5" />
              Về Trang Chủ
            </Button>
          </Link>
        </div>

        {/* Hero Section */}
        <section className="bg-gradient-to-b from-[#ecfdf5] to-white py-16">
          <div className="max-w-[1200px] mx-auto px-6 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-[#111827] mb-4">Hướng dẫn phân loại rác</h1>
            <p className="text-lg text-[#6b7280] max-w-2xl mx-auto">
              Tìm hiểu cách phân loại rác đúng cách để bảo vệ môi trường và tối ưu hóa quy trình tái chế
            </p>
          </div>
        </section>

        {/* Guide Content */}
        <section className="py-16 bg-white">
          <div className="max-w-[800px] mx-auto px-6">
            <div className="space-y-4">
              {wasteCategories.map((category) => (
                <div
                  key={category.id}
                  className="rounded-2xl border-2 overflow-hidden transition-all"
                  style={{ borderColor: category.borderColor }}
                >
                  {/* Category Header */}
                  <button
                    onClick={() => toggleCategory(category.id)}
                    className="w-full px-6 py-5 flex items-center justify-between transition-colors"
                    style={{ backgroundColor: category.bgColor }}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className="w-12 h-12 rounded-xl flex items-center justify-center text-white"
                        style={{ backgroundColor: category.color }}
                      >
                        {category.icon}
                      </div>
                      <div className="text-left">
                        <h2 className="text-xl font-bold" style={{ color: category.color }}>
                          {category.title}
                        </h2>
                        <p className="text-sm text-[#6b7280]">{category.titleEn}</p>
                      </div>
                    </div>
                    <ChevronDown
                      className={cn(
                        "w-6 h-6 transition-transform duration-300",
                        expandedCategory === category.id && "rotate-180",
                      )}
                      style={{ color: category.color }}
                    />
                  </button>

                  {/* Category Items */}
                  <div
                    className={cn(
                      "overflow-hidden transition-all duration-300",
                      expandedCategory === category.id ? "max-h-[2000px]" : "max-h-0",
                    )}
                  >
                    <div className="p-6 space-y-6 bg-white">
                      {category.items.map((item, index) => (
                        <div key={index} className="border-b border-[#e5e7eb] pb-6 last:border-0 last:pb-0">
                          <h3 className="font-bold text-lg text-[#111827] mb-2">{item.name}</h3>
                          <div className="space-y-2">
                            <p className="text-[#6b7280]">
                              <span className="font-medium text-[#374151]">Ví dụ:</span> {item.examples}
                            </p>
                            <p className="text-[#6b7280]">
                              <span className="font-medium text-[#374151]">Mẹo:</span> {item.tips}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Tips Section */}
            <div className="mt-12 p-8 rounded-3xl bg-gradient-to-br from-[#10b981]/10 to-[#3b82f6]/10">
              <h2 className="text-2xl font-bold text-[#111827] mb-6">Mẹo phân loại hiệu quả</h2>
              <ul className="space-y-4">
                {[
                  "Luôn rửa sạch và làm khô vật liệu tái chế trước khi bỏ",
                  "Tách riêng các thành phần nếu sản phẩm làm từ nhiều vật liệu",
                  "Kiểm tra ký hiệu tái chế trên bao bì để biết loại nhựa",
                  "Ép dẹp lon và chai để tiết kiệm không gian trong thùng rác",
                  "Không bỏ rác nguy hại chung với rác thông thường",
                ].map((tip, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[#10b981] text-white text-sm font-bold flex items-center justify-center">
                      {index + 1}
                    </span>
                    <span className="text-[#374151]">{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
