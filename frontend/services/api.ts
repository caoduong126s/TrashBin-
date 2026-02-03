import axios, { type AxiosError } from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

// Backend response type
interface BackendClassificationResponse {
  success: boolean
  data: {
    detections: Array<{
      box: number[]
      confidence: number
      class_name: string
      class_name_en: string
      bin_type: "recyclable" | "general" | "hazardous" | "organic"
      detection_id: number
    }>
    total_objects: number
    processing_time: number
    image_size: { width: number; height: number }
    // ⭐ NEW: Preprocessing info
    preprocessing?: {
      is_low_light: boolean
      method: string
      enhancement_applied: boolean
    }
    // Statistics or other fields if any
    bin_instruction?: string // Not in guide for Classification, but maybe legacy? Keeping optional if uncertain, but Guide doesn't show it.
    recycling_tips?: string[]
    top_3?: Array<{ name: string; confidence: number }>

    // Advanced features might still be directly in data or inside detections? 
    // Guide doesn't show advanced features in the snippet. 
    // Assuming legacy fields might need to be adapted or removed. 
    // I will try to map what I can.
    composite_detected?: boolean
    composite_info?: {
      material_type: string
      matching_classes: string[]
      combined_confidence: number
    }
    low_confidence_warning?: boolean
    suggestions?: string[]
    aggregated_confidence?: number
  }
  error?: string
}

// Frontend type
export interface ClassificationResult {
  className: string
  classNameEn: string
  confidence: number
  binType: "recyclable" | "general" | "hazardous" | "organic"
  binName: string
  instruction: string
  tips: string[]
  topPredictions: Array<{ name: string; confidence: number }>
  processingTime?: number
  // ⭐ NEW: Preprocessing info
  isLowLight?: boolean
  enhancementApplied?: boolean
  // ⭐ NEW: Advanced features
  compositeDetected?: boolean
  compositeInfo?: {
    materialType: string
    matchingClasses: string[]
    combinedConfidence: number
  }
  lowConfidenceWarning?: boolean
  suggestions?: string[]
  aggregatedConfidence?: number
}

// Map bin type to Vietnamese name
const binNameMap: Record<string, string> = {
  recyclable: "Thùng tái chế",
  general: "Thùng rác thường",
  hazardous: "Thùng rác nguy hại",
  organic: "Thùng rác hữu cơ",
}

// Map bin type to instructions
const binInstructionMap: Record<string, string> = {
  recyclable: "Rửa sạch và bỏ vào thùng xanh tái chế",
  general: "Bỏ vào thùng rác màu xám",
  hazardous: "Cần xử lý đặc biệt. Đưa đến điểm thu gom rác nguy hại hoặc liên hệ cơ quan môi trường địa phương",
  organic: "Bỏ vào thùng rác hữu cơ (rau củ, thức ăn thừa) để ủ phân compost",
}

// Recycling tips by class
const recyclingTipsMap: Record<string, string[]> = {
  plastic: [
    "Rửa sạch chai lọ trước khi bỏ vào thùng tái chế",
    "Tháo nắp và nhãn nếu có thể",
    "Không bỏ túi nilon mỏng vào thùng tái chế",
  ],
  glass: [
    "Rửa sạch chai thủy tinh",
    "Tháo nắp kim loại hoặc nhựa",
    "Không bỏ kính vỡ, gương hoặc đồ sứ vào thùng tái chế",
  ],
  paper: [
    "Giữ giấy khô ráo và sạch sẽ",
    "Không tái chế giấy dính băng keo, giấy bóng hoặc giấy dầu mỡ",
    "Gấp gọn hộp giấy trước khi bỏ vào thùng",
  ],
  cardboard: [
    "Làm phẳng hộp carton để tiết kiệm không gian",
    "Loại bỏ băng keo và kim bấm",
    "Giữ carton khô ráo",
  ],
  metal: [
    "Rửa sạch hộp kim loại",
    "Làm phẳng hộp nhôm để tiết kiệm không gian",
    "Tái chế cả nắp kim loại",
  ],
  battery: [
    "KHÔNG bỏ pin vào thùng rác thường",
    "Đưa đến điểm thu gom pin thải chuyên dụng",
    "Pin có thể gây cháy nổ và ô nhiễm môi trường nghiêm trọng",
  ],
  biological: [
    "Phân loại riêng rác hữu cơ để ủ phân compost",
    "Không trộn với nhựa hoặc kim loại",
    "Có thể dùng làm phân bón cho cây",
  ],
  textile: [
    "Quần áo còn tốt có thể quyên góp",
    "Vải vụn có thể tái chế làm vật liệu cách nhiệt",
    "Giặt sạch trước khi quyên góp hoặc tái chế",
  ],
  trash: [
    "Bỏ vào thùng rác thường",
    "Đảm bảo rác được đóng gói kín",
    "Không trộn với rác tái chế hoặc rác nguy hại",
  ],
}

// Transform backend response to frontend format
function transformResponse(data: BackendClassificationResponse["data"]): ClassificationResult {
  const primaryDetection = data.detections && data.detections.length > 0 ? data.detections[0] : null;

  if (!primaryDetection) {
    // Fallback or empty result if no detections
    return {
      className: "Không xác định",
      classNameEn: "unknown",
      confidence: 0,
      binType: "general",
      binName: "Không xác định",
      instruction: "",
      tips: [],
      topPredictions: [],
      processingTime: data.processing_time,
      isLowLight: data.preprocessing?.is_low_light,
      enhancementApplied: data.preprocessing?.enhancement_applied,
    };
  }

  // Convert confidence from decimal (0-1) to percentage (0-100)
  const confidencePercentage = primaryDetection.confidence * 100;

  // Get recycling tips for this class
  const tips = recyclingTipsMap[primaryDetection.class_name_en] || [
    "Phân loại đúng thùng rác",
    "Giữ rác sạch và khô",
    "Tái chế giúp bảo vệ môi trường",
  ];

  // Generate top 3 predictions from all detections
  const topPredictions = data.detections
    .slice(0, 3)
    .map((det) => ({
      name: det.class_name,
      confidence: Math.round(det.confidence * 100 * 10) / 10, // Convert to percentage with 1 decimal
    }));

  return {
    className: primaryDetection.class_name,
    classNameEn: primaryDetection.class_name_en,
    confidence: confidencePercentage,
    binType: primaryDetection.bin_type,
    binName: binNameMap[primaryDetection.bin_type] || "Thùng rác",
    instruction: binInstructionMap[primaryDetection.bin_type] || "",
    tips: tips,
    topPredictions: topPredictions,
    processingTime: data.processing_time,
    // ⭐ NEW: Map preprocessing
    isLowLight: data.preprocessing?.is_low_light,
    enhancementApplied: data.preprocessing?.enhancement_applied,
    // ⭐ NEW: Map advanced features
    compositeDetected: data.composite_detected,
    compositeInfo: data.composite_info ? {
      materialType: data.composite_info.material_type,
      matchingClasses: data.composite_info.matching_classes,
      combinedConfidence: data.composite_info.combined_confidence,
    } : undefined,
    lowConfidenceWarning: data.low_confidence_warning,
    suggestions: data.suggestions,
    aggregatedConfidence: data.aggregated_confidence,
  }
}

// Custom error class for API errors
export class ApiError extends Error {
  code: string
  statusCode?: number

  constructor(message: string, code: string, statusCode?: number) {
    super(message)
    this.name = "ApiError"
    this.code = code
    this.statusCode = statusCode
  }
}

// Classify waste image
export async function classifyWaste(file: File): Promise<ClassificationResult> {
  const formData = new FormData()
  formData.append("file", file)

  try {
    const response = await apiClient.post<BackendClassificationResponse>("/api/v1/classify", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    if (!response.data.success) {
      throw new ApiError(response.data.error || "Classification failed", "CLASSIFICATION_FAILED")
    }

    return transformResponse(response.data.data)
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ error?: string; detail?: string }>

      // Network error
      if (!axiosError.response) {
        console.error("[GreenSort] Network error:", axiosError.message)
        throw new ApiError("Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.", "NETWORK_ERROR")
      }

      const status = axiosError.response.status
      const errorMessage = axiosError.response.data?.error || axiosError.response.data?.detail

      // Handle specific status codes
      if (status === 400) {
        throw new ApiError(
          errorMessage || "File không hợp lệ. Vui lòng chọn ảnh PNG, JPG hoặc JPEG.",
          "VALIDATION_ERROR",
          status,
        )
      }

      if (status === 413) {
        throw new ApiError("File quá lớn. Vui lòng chọn ảnh nhỏ hơn 10MB.", "FILE_TOO_LARGE", status)
      }

      if (status === 401 || status === 403) {
        throw new ApiError("Phiên đăng nhập đã hết hạn. Vui lòng tải lại trang.", "AUTH_ERROR", status)
      }

      if (status === 429) {
        throw new ApiError("Bạn đã gửi quá nhiều yêu cầu. Vui lòng đợi một chút.", "RATE_LIMIT", status)
      }

      if (status >= 500) {
        console.error("[GreenSort] Server error:", status, axiosError.response.data)
        throw new ApiError("Hệ thống đang gặp sự cố. Vui lòng thử lại sau ít phút.", "SERVER_ERROR", status)
      }

      throw new ApiError(errorMessage || "Đã xảy ra lỗi. Vui lòng thử lại.", "UNKNOWN_ERROR", status)
    }

    // Unknown error
    console.error("[GreenSort] Unknown error:", error)
    throw new ApiError("Đã xảy ra lỗi không xác định. Vui lòng thử lại.", "UNKNOWN_ERROR")
  }
}

// ⭐ NEW: Health check function
export async function checkHealth() {
  try {
    const response = await apiClient.get("/api/v1/health")
    return response.data
  } catch (error) {
    console.error("[GreenSort] Health check failed:", error)
    throw new ApiError("Backend không khả dụng", "HEALTH_CHECK_FAILED")
  }
}

// ⭐ NEW: Statistics API Functions

// Statistics response types
interface StatisticsResponse {
  success: boolean
  data: any
  error?: string
}

interface DashboardStats {
  summary: {
    total: { value: number; change: number }
    recyclable: { value: number; change: number }
    accuracy: { value: number; change: number }
    co2_saved: { value: number; change: number }
  }
  trend: Array<{ date: string; count: number }>
  bin_distribution: {
    recyclable: number
    general: number
    hazardous: number
  }
  class_distribution: Record<string, number>
}

interface SummaryStats {
  total_classifications: number
  recyclable_count: number
  accuracy_rate: number
  co2_saved_kg: number
  period_days: number
}

// Get dashboard statistics
export async function getDashboardStats(period: 'today' | 'week' | 'month' = 'week'): Promise<DashboardStats> {
  try {
    const response = await apiClient.get<StatisticsResponse>(`/api/v1/statistics/dashboard?period=${period}`)

    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Failed to fetch dashboard stats', 'STATS_FAILED')
    }

    return response.data.data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (axios.isAxiosError(error)) {
      console.error('[GreenSort] Dashboard stats error:', error.message)
      throw new ApiError('Không thể tải thống kê dashboard', 'STATS_ERROR')
    }

    throw new ApiError('Đã xảy ra lỗi khi tải thống kê', 'UNKNOWN_ERROR')
  }
}

// Get summary statistics
export async function getSummaryStats(): Promise<any> {
  try {
    const response = await apiClient.get<StatisticsResponse>('/api/v1/stats/summary')

    if (!response.data.success && response.data.error) { // The guide response example doesn't have 'success' wrapper for this endpoint? Spec says "Response: { ... }". Assuming standard wrapper or direct json.
      // Actually spec format: { "total_classifications": ... } direct object?
      // Guide says "Response ```json { ... } ```"
      // But other endpoints show { "success": true, "data": ... }
      // The Spec for stats/summary just shows the data object.
      // However, usually APIs are consistent. I will assume it might be wrapped OR plain.
      // Let's assume it returns the data directly as per the example block which lacks "success: true".
      // But to be safe with existing helper patterns, I'll return response.data.
    }

    return response.data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (axios.isAxiosError(error)) {
      console.error('[GreenSort] Summary stats error:', error.message)
      throw new ApiError('Không thể tải tổng quan thống kê', 'STATS_ERROR')
    }

    throw new ApiError('Đã xảy ra lỗi khi tải thống kê', 'UNKNOWN_ERROR')
  }
}

// ⭐ NEW: Submit User Feedback
export interface FeedbackPayload {
  classification_id?: number
  is_correct: boolean
  correct_class?: string
  user_comment?: string
}

export async function submitFeedback(payload: FeedbackPayload): Promise<void> {
  try {
    await apiClient.post('/api/v1/feedback/submit', payload)
  } catch (error) {
    console.error('[GreenSort] Feedback error:', error)
    // Don't throw for feedback, just log
  }
}

// ⭐ NEW: Submit Crowdsource Image
export async function submitCrowdsourceImage(file: File, label: string, userId?: string): Promise<void> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_label', label)
  if (userId) formData.append('user_id', userId)

  try {
    await apiClient.post('/api/v1/crowdsource/submit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  } catch (error) {
    console.error('[GreenSort] Crowdsource error:', error)
    throw new ApiError('Không thể gửi ảnh đóng góp. Vui lòng thử lại.', 'UPLOAD_ERROR')
  }
}

// Get trend data
export async function getTrendData(days: number = 7): Promise<Array<{ date: string; count: number }>> {
  try {
    const response = await apiClient.get<StatisticsResponse>(`/api/v1/statistics/trend?days=${days}`)

    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Failed to fetch trend', 'STATS_FAILED')
    }

    return response.data.data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (axios.isAxiosError(error)) {
      console.error('[GreenSort] Trend data error:', error.message)
      throw new ApiError('Không thể tải dữ liệu xu hướng', 'STATS_ERROR')
    }

    throw new ApiError('Đã xảy ra lỗi khi tải xu hướng', 'UNKNOWN_ERROR')
  }
}

// Get bin distribution
export async function getBinDistribution(days?: number): Promise<{
  recyclable: number
  general: number
  hazardous: number
}> {
  try {
    const url = days ? `/api/v1/statistics/distribution/bins?days=${days}` : '/api/v1/statistics/distribution/bins'
    const response = await apiClient.get<StatisticsResponse>(url)

    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Failed to fetch bin distribution', 'STATS_FAILED')
    }

    return response.data.data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (axios.isAxiosError(error)) {
      console.error('[GreenSort] Bin distribution error:', error.message)
      throw new ApiError('Không thể tải phân bố thùng rác', 'STATS_ERROR')
    }

    throw new ApiError('Đã xảy ra lỗi khi tải phân bố', 'UNKNOWN_ERROR')
  }
}

/**
 * Recycling Locations
 */
export interface RecyclingLocation {
  id: number
  name: string
  address: string
  latitude: number
  longitude: number
  waste_types: string
  operating_hours?: string
  contact_phone?: string
  description?: string
  created_at: string
}

export const getLocations = async (wasteType?: string): Promise<RecyclingLocation[]> => {
  try {
    const response = await apiClient.get("/api/v1/locations/", {
      params: { waste_type: wasteType },
    })
    return response.data
  } catch (error) {
    console.error("Error fetching locations:", error)
    return []
  }
}

export const seedLocations = async (): Promise<{ message: string }> => {
  try {
    const response = await apiClient.post("/api/v1/locations/seed")
    return response.data
  } catch (error) {
    console.error("Error seeding locations:", error)
    throw error
  }
}

// Get class distribution
export async function getClassDistribution(
  days?: number,
  topN: number = 4
): Promise<Record<string, number>> {
  try {
    const params = new URLSearchParams()
    if (days) params.append('days', days.toString())
    params.append('top_n', topN.toString())

    const response = await apiClient.get<StatisticsResponse>(
      `/api/v1/statistics/distribution/classes?${params.toString()}`
    )

    if (!response.data.success) {
      throw new ApiError(response.data.error || 'Failed to fetch class distribution', 'STATS_FAILED')
    }

    return response.data.data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    if (axios.isAxiosError(error)) {
      console.error('[GreenSort] Class distribution error:', error.message)
      throw new ApiError('Không thể tải phân bố loại rác', 'STATS_ERROR')
    }

    throw new ApiError('Đã xảy ra lỗi khi tải phân bố', 'UNKNOWN_ERROR')
  }
}