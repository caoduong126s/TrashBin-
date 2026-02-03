"use client"

import type React from "react"

import { useState, useCallback, useRef, useEffect } from "react"
import { Upload, X, Check, Loader2, Camera, SwitchCamera, CircleStop, RotateCcw, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { toast } from "@/hooks/use-toast"

interface UploadSectionProps {
  onImageSelect: (file: File) => void
  onClassify: () => void
  selectedImage: File | null
  imagePreview: string | null
  isAnalyzing: boolean
  error?: string | null
  onRetry?: () => void
}

type TabType = "upload" | "camera" | "samples"

const sampleImages = [
  {
    name: "Chai nhựa",
    url: "/plastic-bottle-recyclable.jpg",
  },
  { name: "Lon nhôm", url: "/aluminum-can-recyclable.jpg" },
  { name: "Hộp giấy", url: "/cardboard-box-recyclable.jpg" },
  { name: "Pin cũ", url: "/old-battery-hazardous-waste.jpg" },
]

export function UploadSection({
  onImageSelect,
  onClassify,
  selectedImage,
  imagePreview,
  isAnalyzing,
  error,
  onRetry,
}: UploadSectionProps) {
  const [activeTab, setActiveTab] = useState<TabType>("upload")
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [facingMode, setFacingMode] = useState<"user" | "environment">("environment")
  const streamRef = useRef<MediaStream | null>(null)

  const startCamera = useCallback(async () => {
    setCameraError(null)
    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }

      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        setIsCameraActive(true)
        toast({
          title: "Camera đã sẵn sàng",
          description: "Đặt rác thải vào giữa khung hình và nhấn chụp",
          variant: "success",
        })
      }
    } catch (err) {
      console.error("[GreenSort] Camera initialization error:", err)

      let errorMessage = "Không thể khởi động camera. Vui lòng thử lại."

      if (err instanceof Error) {
        if (err.name === "NotAllowedError") {
          errorMessage = "Vui lòng cho phép truy cập camera để sử dụng tính năng này"
        } else if (err.name === "NotFoundError") {
          errorMessage = "Không tìm thấy camera trên thiết bị của bạn"
        } else if (err.name === "NotReadableError") {
          errorMessage = "Camera đang được sử dụng bởi ứng dụng khác"
        }
        console.error("[GreenSort] Camera error details:", { name: err.name, message: err.message })
      }

      setCameraError(errorMessage)
      toast({
        title: "Lỗi camera",
        description: errorMessage,
        variant: "destructive",
      })
      setIsCameraActive(false)
    }
  }, [facingMode])

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setIsCameraActive(false)
  }, [])

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext("2d")

    if (!context) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    canvas.toBlob(
      (blob) => {
        if (blob) {
          const file = new File([blob], `camera-capture-${Date.now()}.jpg`, {
            type: "image/jpeg",
          })
          onImageSelect(file)
          stopCamera()
          toast({
            title: "Chụp ảnh thành công",
            description: "Ảnh đã sẵn sàng để phân loại",
            variant: "success",
          })
        } else {
          console.error("[GreenSort] Failed to capture photo: blob is null")
          toast({
            title: "Lỗi chụp ảnh",
            description: "Không thể chụp ảnh. Vui lòng thử lại.",
            variant: "destructive",
          })
        }
      },
      "image/jpeg",
      0.9,
    )
  }, [onImageSelect, stopCamera])

  const switchCamera = useCallback(() => {
    setFacingMode((prev) => (prev === "user" ? "environment" : "user"))
  }, [])

  useEffect(() => {
    if (isCameraActive) {
      startCamera()
    }
  }, [facingMode])

  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [stopCamera])

  useEffect(() => {
    if (activeTab !== "camera") {
      stopCamera()
    }
  }, [activeTab, stopCamera])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const files = e.dataTransfer.files
      if (files.length > 0) {
        const file = files[0]
        if (file.type.startsWith("image/")) {
          if (file.size > 5 * 1024 * 1024) {
            console.error("[GreenSort] File too large:", file.size)
            toast({
              title: "File quá lớn",
              description: "Vui lòng chọn ảnh có kích thước nhỏ hơn 5MB",
              variant: "destructive",
            })
            return
          }
          onImageSelect(file)
          toast({
            title: "Tải ảnh thành công",
            description: `Đã chọn: ${file.name}`,
            variant: "success",
          })
        } else {
          console.error("[GreenSort] Invalid file type:", file.type)
          toast({
            title: "Định dạng không hỗ trợ",
            description: "Vui lòng chọn file ảnh (JPG, PNG, WEBP)",
            variant: "destructive",
          })
        }
      }
    },
    [onImageSelect],
  )

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        const file = files[0]
        if (file.size > 5 * 1024 * 1024) {
          console.error("[GreenSort] File too large:", file.size)
          toast({
            title: "File quá lớn",
            description: "Vui lòng chọn ảnh có kích thước nhỏ hơn 5MB",
            variant: "destructive",
          })
          return
        }
        onImageSelect(file)
        toast({
          title: "Tải ảnh thành công",
          description: `Đã chọn: ${file.name}`,
          variant: "success",
        })
      }
    },
    [onImageSelect],
  )

  const handleSampleSelect = useCallback(
    async (url: string, name: string) => {
      try {
        const response = await fetch(url)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const blob = await response.blob()
        const file = new File([blob], `${name}.jpg`, { type: "image/jpeg" })
        onImageSelect(file)
        toast({
          title: "Đã chọn ảnh mẫu",
          description: `Đang sử dụng: ${name}`,
          variant: "success",
        })
      } catch (err) {
        console.error("[GreenSort] Failed to load sample image:", err)
        toast({
          title: "Lỗi tải ảnh mẫu",
          description: "Không thể tải ảnh mẫu. Vui lòng thử lại hoặc chọn ảnh khác.",
          variant: "destructive",
        })
      }
    },
    [onImageSelect],
  )

  const tabs: { id: TabType; label: string }[] = [
    { id: "upload", label: "Upload" },
    { id: "camera", label: "Camera" },
    { id: "samples", label: "Mẫu" },
  ]

  return (
    <section className="py-20 bg-white dark:bg-gray-800">
      <div className="max-w-[800px] mx-auto px-6">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl animate-fade-in-up">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h4 className="font-medium text-red-800 dark:text-red-200">Đã xảy ra lỗi</h4>
                <p className="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
              </div>
              {onRetry && (
                <Button
                  onClick={onRetry}
                  variant="outline"
                  size="sm"
                  className="border-red-300 dark:border-red-700 text-red-600 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/30 bg-transparent"
                >
                  <RotateCcw className="w-4 h-4 mr-1" />
                  Thử lại
                </Button>
              )}
            </div>
          </div>
        )}

        <div className="flex justify-center gap-2 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "px-6 py-3 text-base font-medium transition-all rounded-lg",
                activeTab === tab.id
                  ? "text-[#10b981] border-b-[3px] border-[#10b981] bg-[#ecfdf5] dark:bg-[#10b981]/20"
                  : "text-[#6b7280] dark:text-gray-400 hover:text-[#10b981] hover:bg-[#f9fafb] dark:hover:bg-gray-700",
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "upload" && !imagePreview && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all",
              isDragging
                ? "border-[#10b981] bg-[#d1fae5] dark:bg-[#10b981]/20"
                : "border-[#e5e7eb] dark:border-gray-600 bg-[#f9fafb] dark:bg-gray-700 hover:border-[#10b981] hover:bg-[#ecfdf5] dark:hover:bg-[#10b981]/10",
            )}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Upload
              className={cn(
                "w-16 h-16 mx-auto mb-4 transition-colors",
                isDragging ? "text-[#10b981]" : "text-[#9ca3af] dark:text-gray-400",
              )}
            />
            <p className="text-lg font-medium text-[#374151] dark:text-gray-200 mb-2">
              Kéo thả ảnh vào đây hoặc click để chọn
            </p>
            <p className="text-sm text-[#6b7280] dark:text-gray-400">JPG, PNG, WEBP - Tối đa 5MB</p>
          </div>
        )}

        {activeTab === "camera" && !imagePreview && (
          <div className="space-y-4">
            <canvas ref={canvasRef} className="hidden" />

            {!isCameraActive ? (
              <div className="border-2 border-dashed border-[#e5e7eb] dark:border-gray-600 rounded-xl p-16 text-center bg-[#f9fafb] dark:bg-gray-700">
                {cameraError ? (
                  <>
                    <div className="w-16 h-16 mx-auto mb-4 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                      <X className="w-8 h-8 text-red-500" />
                    </div>
                    <p className="text-lg font-medium text-[#374151] dark:text-gray-200 mb-2">Lỗi camera</p>
                    <p className="text-sm text-red-500 mb-4">{cameraError}</p>
                    <Button onClick={startCamera} className="bg-[#10b981] hover:bg-[#059669] text-white">
                      Thử lại
                    </Button>
                  </>
                ) : (
                  <>
                    <div className="w-16 h-16 mx-auto mb-4 bg-[#ecfdf5] dark:bg-[#10b981]/20 rounded-full flex items-center justify-center">
                      <Camera className="w-8 h-8 text-[#10b981]" />
                    </div>
                    <p className="text-lg font-medium text-[#374151] dark:text-gray-200 mb-2">Chụp ảnh từ camera</p>
                    <p className="text-sm text-[#6b7280] dark:text-gray-400 mb-6">
                      Chụp trực tiếp rác thải để phân loại ngay lập tức
                    </p>
                    <Button
                      onClick={startCamera}
                      className="bg-[#10b981] hover:bg-[#059669] text-white px-8 py-3 h-auto text-base font-medium"
                    >
                      <Camera className="w-5 h-5 mr-2" />
                      Bật Camera
                    </Button>
                  </>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-xl overflow-hidden bg-black aspect-[4/3] max-w-[500px] mx-auto">
                  <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />

                  <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute inset-8 border-2 border-white/30 rounded-lg" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 border-2 border-[#10b981] rounded-full opacity-50" />
                  </div>

                  <button
                    onClick={switchCamera}
                    className="absolute top-4 right-4 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-colors"
                    aria-label="Chuyển camera"
                  >
                    <SwitchCamera className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex items-center justify-center gap-4">
                  <Button
                    onClick={stopCamera}
                    variant="outline"
                    className="px-6 py-3 h-auto text-base font-medium border-[#e5e7eb] dark:border-gray-600 text-[#6b7280] dark:text-gray-300 hover:bg-[#f9fafb] dark:hover:bg-gray-700 bg-transparent"
                  >
                    <CircleStop className="w-5 h-5 mr-2" />
                    Dừng
                  </Button>
                  <Button
                    onClick={capturePhoto}
                    className="bg-[#10b981] hover:bg-[#059669] text-white px-8 py-3 h-auto text-base font-medium shadow-lg hover:shadow-xl transition-all"
                  >
                    <Camera className="w-5 h-5 mr-2" />
                    Chụp ảnh
                  </Button>
                </div>

                <p className="text-center text-sm text-[#6b7280] dark:text-gray-400">
                  Đặt rác thải vào giữa khung hình và nhấn "Chụp ảnh"
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === "samples" && !imagePreview && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {sampleImages.map((sample) => (
              <button
                key={sample.name}
                onClick={() => handleSampleSelect(sample.url, sample.name)}
                className="group relative aspect-square rounded-xl overflow-hidden border-2 border-[#e5e7eb] dark:border-gray-600 hover:border-[#10b981] transition-all"
              >
                <img
                  src={sample.url || "/placeholder.svg"}
                  alt={sample.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <p className="absolute bottom-3 left-3 text-white font-medium text-sm">{sample.name}</p>
              </button>
            ))}
          </div>
        )}

        {imagePreview && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="relative max-w-[400px] mx-auto">
              <img
                src={imagePreview || "/placeholder.svg"}
                alt="Preview"
                className="w-full aspect-square object-cover rounded-2xl shadow-lg"
              />
              <button
                onClick={() => onImageSelect(null as unknown as File)}
                className="absolute top-3 right-3 w-8 h-8 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-colors"
                aria-label="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-center space-y-3">
              <div className="flex items-center justify-center gap-2 text-[#10b981]">
                <Check className="w-5 h-5" />
                <span className="font-medium">Sẵn sàng</span>
              </div>
              <p className="text-sm text-[#6b7280] dark:text-gray-400">
                {selectedImage?.name} - {((selectedImage?.size || 0) / 1024 / 1024).toFixed(2)}MB
              </p>
              <Button
                onClick={onClassify}
                disabled={isAnalyzing}
                className="bg-[#10b981] hover:bg-[#059669] text-white px-8 py-3 h-auto text-base font-medium rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-70"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Đang phân tích...
                  </>
                ) : (
                  <>
                    <span className="mr-2">🔍</span>
                    Phân loại ngay
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
