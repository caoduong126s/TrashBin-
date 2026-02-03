"use client"

import { useState, useEffect } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { TrendingUp, Recycle, CheckCircle, Leaf, Home, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from "recharts"
import { getDashboardStats } from "@/services/api"

type TimeRange = "today" | "week" | "month"

// ⭐ Remove hard-coded data - will load from API

export default function StatisticsPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>("week")
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const timeRanges: { id: TimeRange; label: string }[] = [
    { id: "today", label: "Hôm nay" },
    { id: "week", label: "Tuần" },
    { id: "month", label: "Tháng" },
  ]

  //  Load data from API
  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true)
        setError(null)

        console.log('[GreenSort] Loading dashboard stats for period:', timeRange)
        const data = await getDashboardStats(timeRange)
        console.log('[GreenSort] Dashboard stats loaded:', data)

        setStats(data)
      } catch (err: any) {
        console.error('[GreenSort] Failed to load dashboard stats:', err)
        setError(err.message || 'Không thể tải thống kê')
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [timeRange])

  //  Transform API data to component format
  const getStatsCards = () => {
    if (!stats) return []

    return [
      {
        icon: TrendingUp,
        label: "TỔNG SỐ",
        value: stats.summary.total.value.toLocaleString(),
        trend: `${stats.summary.total.change >= 0 ? '+' : ''}${stats.summary.total.change}%`,
        trendUp: stats.summary.total.change >= 0,
        color: "#10b981",
        bgColor: "#ecfdf5",
      },
      {
        icon: Recycle,
        label: "TÁI CHẾ",
        value: stats.summary.recyclable.value.toLocaleString(),
        trend: `${stats.summary.recyclable.change >= 0 ? '+' : ''}${stats.summary.recyclable.change}%`,
        trendUp: stats.summary.recyclable.change >= 0,
        color: "#3b82f6",
        bgColor: "#eff6ff",
      },
      {
        icon: CheckCircle,
        label: "CHÍNH XÁC",
        value: `${stats.summary.accuracy.value}%`,
        trend: `${stats.summary.accuracy.change >= 0 ? '+' : ''}${stats.summary.accuracy.change}%`,
        trendUp: stats.summary.accuracy.change >= 0,
        color: "#10b981",
        bgColor: "#ecfdf5",
      },
      {
        icon: Leaf,
        label: "TIẾT KIỆM",
        value: `${stats.summary.co2_saved.value}kg`,
        trend: `${stats.summary.co2_saved.change >= 0 ? '+' : ''}${stats.summary.co2_saved.change}%`,
        trendUp: stats.summary.co2_saved.change >= 0,
        color: "#059669",
        bgColor: "#d1fae5",
        subLabel: "CO2",
      },
    ]
  }

  //  Transform bin distribution data
  const getBinDistribution = () => {
    if (!stats) return []

    return [
      { name: "Tái chế", value: stats.bin_distribution.recyclable, color: "#3b82f6" },
      { name: "Thông thường", value: stats.bin_distribution.general, color: "#6b7280" },
      { name: "Nguy hại", value: stats.bin_distribution.hazardous, color: "#ef4444" },
      { name: "Hữu cơ", value: stats.bin_distribution.organic, color: "#f59e0b" },
    ]
  }

  // ⭐ Transform class distribution data
  const getCategoryData = () => {
    if (!stats) return []

    const classData = Object.entries(stats.class_distribution).map(([name, count]) => ({
      name,
      count: count as number,
      percentage: 0, // Will calculate if needed
    }))

    return classData
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#f9fafb]">
      <Header />

      <main className="flex-1 py-12">
        <div className="max-w-[1200px] mx-auto px-6">
          {/* Quick Home Button */}
          <div className="mb-6">
            <Link href="/">
              <Button variant="ghost" className="text-green-700 hover:text-green-800 hover:bg-green-50 font-bold gap-2 p-0">
                <Home className="w-5 h-5" />
                Về Trang Chủ
              </Button>
            </Link>
          </div>

          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-[#111827]">Bảng điều khiển</h1>
              <p className="text-[#6b7280] mt-1">Thống kê hoạt động phân loại rác cộng đồng</p>
            </div>
            <div className="flex gap-2 bg-white rounded-lg p-1 shadow-sm">
              {timeRanges.map((range) => (
                <button
                  key={range.id}
                  onClick={() => setTimeRange(range.id)}
                  disabled={loading}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${timeRange === range.id
                    ? "bg-[#10b981] text-white"
                    : "text-[#6b7280] hover:text-[#111827] hover:bg-[#f3f4f6]"
                    } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#10b981] mx-auto mb-4"></div>
                <p className="text-[#6b7280]">Đang tải thống kê...</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <p className="text-red-800 font-medium mb-4">❌ {error}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Thử lại
              </button>
            </div>
          )}

          {/* Stats Content */}
          {stats && !loading && !error && (
            <>
              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {getStatsCards().map((stat, index) => (
                  <div
                    key={index}
                    className="bg-white rounded-2xl p-6 shadow-md hover:shadow-lg transition-all hover:scale-[1.02] cursor-default"
                  >
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                      style={{ backgroundColor: stat.bgColor }}
                    >
                      <stat.icon className="w-6 h-6" style={{ color: stat.color }} />
                    </div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-[#6b7280] mb-1">{stat.label}</p>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl font-bold text-[#111827]">{stat.value}</span>
                      {stat.subLabel && <span className="text-sm text-[#6b7280]">{stat.subLabel}</span>}
                    </div>
                    <div className="flex items-center gap-1 mt-2">
                      <span className={`text-sm font-medium ${stat.trendUp ? "text-[#10b981]" : "text-[#ef4444]"}`}>
                        {stat.trend} {stat.trendUp ? "↗" : "↘"}
                      </span>
                      <span className="text-xs text-[#9ca3af]">so với tuần trước</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Line Chart */}
                <div className="bg-white rounded-2xl p-6 shadow-md">
                  <h3 className="text-lg font-bold text-[#111827] mb-6">Xu hướng tuần qua</h3>
                  {stats.trend && stats.trend.length > 0 ? (
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={stats.trend}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                          <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                          <YAxis axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#fff",
                              border: "1px solid #e5e7eb",
                              borderRadius: "8px",
                              boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                            }}
                            formatter={(value) => [`${value} mẫu`, "Số lượng"]}
                          />
                          <Line
                            type="monotone"
                            dataKey="count"
                            stroke="#10b981"
                            strokeWidth={4}
                            dot={{ fill: "#fff", stroke: "#10b981", strokeWidth: 2, r: 6 }}
                            activeDot={{ r: 8, fill: "#10b981" }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-[#6b7280]">
                      Chưa có dữ liệu xu hướng
                    </div>
                  )}
                </div>

                {/* Pie Chart */}
                <div className="bg-white rounded-2xl p-6 shadow-md">
                  <h3 className="text-lg font-bold text-[#111827] mb-6">Thống kê thùng rác</h3>
                  <div className="h-[300px] flex items-center">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getBinDistribution()}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={4}
                          dataKey="value"
                        >
                          {getBinDistribution().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#fff",
                            border: "1px solid #e5e7eb",
                            borderRadius: "8px",
                            boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                          }}
                          formatter={(value) => [`${value} mẫu`, "Số lượng"]}
                        />
                        <Legend
                          verticalAlign="middle"
                          align="right"
                          layout="vertical"
                          iconType="circle"
                          formatter={(value) => <span className="text-[#374151] text-sm">{value}</span>}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Bar Chart */}
              {getCategoryData().length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-md">
                  <h3 className="text-lg font-bold text-[#111827] mb-6">Phân phối theo loại</h3>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getCategoryData()} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
                        <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                        <YAxis
                          type="category"
                          dataKey="name"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#374151", fontSize: 14 }}
                          width={80}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#fff",
                            border: "1px solid #e5e7eb",
                            borderRadius: "8px",
                            boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                          }}
                          formatter={(value) => [`${value} mẫu`, "Số lượng"]}
                        />
                        <Bar dataKey="count" fill="#3b82f6" radius={[0, 10, 10, 0]} barSize={40} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}