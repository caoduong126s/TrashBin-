const features = [
  {
    icon: "🎯",
    title: "Chính xác cao",
    description: "Độ chính xác lên đến 95.5% với mô hình AI tiên tiến",
  },
  {
    icon: "📊",
    title: "Thống kê chi tiết",
    description: "Theo dõi lịch sử phân loại và đóng góp của bạn cho môi trường",
  },
  {
    icon: "🌍",
    title: "Thân thiện môi trường",
    description: "Giảm lượng CO2 thải ra bằng cách phân loại rác đúng cách",
  },
]

export function FeaturesSection() {
  return (
    <section className="py-20 bg-white dark:bg-gray-800">
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-[#111827] dark:text-white mb-12">
          Tính năng nổi bật
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-10 rounded-3xl bg-gradient-to-br from-[#10b981]/10 to-[#3b82f6]/10 dark:from-[#10b981]/20 dark:to-[#3b82f6]/20 hover:shadow-xl hover:scale-105 transition-all duration-300 cursor-default"
            >
              <div className="text-6xl mb-6">{feature.icon}</div>
              <h3 className="text-2xl font-bold text-[#111827] dark:text-white mb-3">{feature.title}</h3>
              <p className="text-[#6b7280] dark:text-gray-300 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
