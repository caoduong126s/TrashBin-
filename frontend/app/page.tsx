"use client"

import { useState, useCallback } from "react"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { HeroSection } from "@/components/hero-section"
import { UploadSection } from "@/components/upload-section"
import { ClassificationResultSection, type ClassificationResult } from "@/components/classification-result"
import { BinVisualization } from "@/components/bin-visualization"
import { FeaturesSection } from "@/components/features-section"
import { HowItWorks } from "@/components/how-it-works"
import { toast } from "@/hooks/use-toast"
import { classifyWaste, ApiError } from "@/services/api"

export default function HomePage() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<ClassificationResult | null>(null)
  const [activeBin, setActiveBin] = useState<"recyclable" | "general" | "hazardous" | "organic" | null>(null)
  const [classificationError, setClassificationError] = useState<string | null>(null)

  const handleImageSelect = useCallback((file: File | null) => {
    setClassificationError(null)

    if (file) {
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string)
      }
      reader.onerror = () => {
        console.error("[GreenSort] Error reading file:", reader.error)
        toast({
          title: "Lỗi đọc file",
          description: "Không thể đọc file ảnh. Vui lòng thử lại với file khác.",
          variant: "destructive",
        })
      }
      reader.readAsDataURL(file)
      setResult(null)
      setActiveBin(null)
    } else {
      setSelectedImage(null)
      setImagePreview(null)
      setResult(null)
      setActiveBin(null)
    }
  }, [])

  const handleClassify = useCallback(async () => {
    if (!selectedImage) return

    setIsAnalyzing(true)
    setClassificationError(null)

    try {
      // Call real FastAPI backend
      const classificationResult = await classifyWaste(selectedImage)

      setResult(classificationResult)
      setActiveBin(classificationResult.binType)

      toast({
        title: "Phân loại thành công",
        description: `Đã nhận diện: ${classificationResult.className} (${classificationResult.confidence.toFixed(1)}%)`,
        variant: "success",
      })

      setTimeout(() => {
        document.getElementById("result-section")?.scrollIntoView({ behavior: "smooth" })
      }, 100)
    } catch (err) {
      console.error("[GreenSort] Classification API error:", err)

      let errorMessage = "Không thể phân loại ảnh. Vui lòng thử lại."

      if (err instanceof ApiError) {
        errorMessage = err.message
        console.error("[GreenSort] API Error details:", {
          code: err.code,
          statusCode: err.statusCode,
          message: err.message,
        })
      } else if (err instanceof Error) {
        console.error("[GreenSort] Error details:", { message: err.message, stack: err.stack })
      }

      setClassificationError(errorMessage)
      toast({
        title: "Lỗi phân loại",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }, [selectedImage])

  const handleRetry = useCallback(() => {
    setClassificationError(null)
    handleClassify()
  }, [handleClassify])

  const handleClassifyAgain = useCallback(() => {
    setSelectedImage(null)
    setImagePreview(null)
    setResult(null)
    setActiveBin(null)
    setClassificationError(null)
    window.scrollTo({ top: 0, behavior: "smooth" })
  }, [])

  const scrollToUpload = useCallback(() => {
    document.getElementById("upload-section")?.scrollIntoView({ behavior: "smooth" })
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        <HeroSection onUploadClick={scrollToUpload} onCameraClick={scrollToUpload} onSampleClick={scrollToUpload} />

        <div id="upload-section">
          <UploadSection
            onImageSelect={handleImageSelect}
            onClassify={handleClassify}
            selectedImage={selectedImage}
            imagePreview={imagePreview}
            isAnalyzing={isAnalyzing}
            error={classificationError}
            onRetry={handleRetry}
          />
        </div>

        {result && imagePreview && (
          <div id="result-section">
            <ClassificationResultSection
              result={result}
              imagePreview={imagePreview}
              onClassifyAgain={handleClassifyAgain}
            />
          </div>
        )}

        <BinVisualization activeBin={activeBin} />

        <FeaturesSection />

        <HowItWorks />
      </main>

      <Footer />
    </div>
  )
}
