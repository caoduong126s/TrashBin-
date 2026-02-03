const steps = [
  {
    number: 1,
    icon: "📤",
    title: "Upload ảnh",
    description: "Chọn hoặc chụp ảnh rác cần phân loại",
  },
  {
    number: 2,
    icon: "🤖",
    title: "AI phân tích",
    description: "Hệ thống AI xử lý và nhận diện loại rác",
  },
  {
    number: 3,
    icon: "♻️",
    title: "Nhận hướng dẫn",
    description: "Biết cách xử lý và tái chế đúng cách",
  },
]

export function HowItWorks() {
  return (
    <section className="py-20 bg-gradient-to-b from-[#ecfdf5] to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-[1200px] mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-[#111827] dark:text-white mb-16">
          Cách sử dụng
        </h2>

        <div className="relative">
          {/* Timeline connector - hidden on mobile */}
          <div className="hidden md:block absolute top-[60px] left-[calc(16.67%+40px)] right-[calc(16.67%+40px)] h-0.5 bg-[#e5e7eb] dark:bg-gray-600" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {steps.map((step) => (
              <div key={step.number} className="flex flex-col items-center text-center relative">
                {/* Number Circle */}
                <div className="w-20 h-20 rounded-full bg-[#10b981] flex items-center justify-center mb-6 shadow-lg relative z-10">
                  <span className="text-3xl font-bold text-white">{step.number}</span>
                </div>

                {/* Icon */}
                <div className="text-4xl mb-4">{step.icon}</div>

                {/* Content */}
                <h3 className="text-xl font-bold text-[#111827] dark:text-white mb-2">{step.title}</h3>
                <p className="text-[#6b7280] dark:text-gray-300">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
