import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Target, Eye, Home } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"


const values = [
  {
    icon: Target,
    title: "Sứ mệnh",
    description:
      "Nâng cao nhận thức cộng đồng về phân loại rác tại nguồn, góp phần bảo vệ môi trường và xây dựng lối sống bền vững cho thế hệ tương lai.",
    color: "#10b981",
    bgColor: "#ecfdf5",
  },
  {
    icon: Eye,
    title: "Tầm nhìn 2030",
    description:
      "Trở thành nền tảng phân loại rác thông minh phổ biến nhất Việt Nam, với mục tiêu giảm 50% lượng rác thải không được phân loại đúng cách.",
    color: "#3b82f6",
    bgColor: "#eff6ff",
  },
]

export default function AboutPage() {
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
        <section className="bg-gradient-to-b from-[#ecfdf5] to-white py-20">
          <div className="max-w-[1200px] mx-auto px-6 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-[#111827] mb-6">Về GreenSort</h1>
            <p className="text-lg text-[#6b7280] max-w-3xl mx-auto leading-relaxed">
              GreenSort được thành lập với mục tiêu đơn giản hóa việc phân loại rác thải tại nguồn thông qua sức mạnh
              của AI. Chúng tôi tin rằng mỗi hành động nhỏ trong việc xử lý rác đúng cách sẽ góp phần tạo nên sự thay
              đổi lớn cho môi trường.
            </p>
          </div>
        </section>

        {/* Mission & Vision */}
        <section className="py-20 bg-white">
          <div className="max-w-[1200px] mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {values.map((value, index) => (
                <div
                  key={index}
                  className="p-8 rounded-3xl border border-[#e5e7eb] hover:shadow-xl transition-all"
                  style={{ backgroundColor: value.bgColor }}
                >
                  <div
                    className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
                    style={{ backgroundColor: value.color }}
                  >
                    <value.icon className="w-8 h-8 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-[#111827] mb-4">{value.title}</h2>
                  <p className="text-[#6b7280] leading-relaxed">{value.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>



        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-[#10b981] to-[#059669]">
          <div className="max-w-[1200px] mx-auto px-6 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Cùng chung tay bảo vệ môi trường</h2>
            <p className="text-white/80 mb-8 max-w-2xl mx-auto">
              Mỗi hành động nhỏ của bạn đều tạo nên sự khác biệt lớn. Hãy bắt đầu phân loại rác đúng cách ngay hôm nay!
            </p>
            <a
              href="/"
              className="inline-flex items-center gap-2 bg-white text-[#10b981] px-8 py-4 rounded-xl font-semibold hover:shadow-lg hover:scale-105 transition-all"
            >
              Bắt đầu ngay
            </a>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
