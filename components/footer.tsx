import Link from "next/link"
import { Leaf } from "lucide-react"

const quickLinks = [
  { href: "/", label: "Trang chủ" },
  { href: "/about", label: "Về chúng tôi" },
  { href: "/statistics", label: "Thống kê" },
  { href: "/guide", label: "Hướng dẫn" },
]

const socialLinks = [
  { href: "#", label: "Facebook", icon: "FB" },
  { href: "#", label: "Instagram", icon: "IG" },
  { href: "#", label: "Twitter", icon: "TW" },
]

export function Footer() {
  return (
    <footer className="bg-[#1f2937] dark:bg-gray-950 text-white">
      <div className="max-w-[1200px] mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* About Column */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#10b981] rounded-lg flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">GreenSort</span>
            </Link>
            <p className="text-[#9ca3af] text-base leading-relaxed max-w-[300px]">
              Công cụ phân loại rác thông minh ứng dụng trí tuệ nhân tạo, giúp cộng đồng bảo vệ môi trường và tối ưu hóa
              quy trình tái chế.
            </p>
          </div>

          {/* Quick Links Column */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold">Liên kết nhanh</h3>
            <nav className="flex flex-col gap-3">
              {quickLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-[#9ca3af] hover:text-[#10b981] transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* Social Column */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold">Theo dõi chúng tôi</h3>
            <div className="flex gap-3">
              {socialLinks.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-sm font-medium hover:bg-[#10b981] transition-colors"
                  aria-label={link.label}
                >
                  {link.icon}
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-12 pt-6 border-t border-white/10 text-center">
          <p className="text-[#6b7280] text-sm">© 2026 GreenSort. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
