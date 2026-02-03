"use client"

import { useState } from "react"
import { ThumbsUp, ThumbsDown, AlertCircle, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { submitFeedback } from "@/services/api"
import { useToast } from "@/hooks/use-toast"

interface ClassificationFeedbackProps {
    classificationId?: number
    detectedClass: string
    detectedClassEn: string
}

const WASTE_CLASSES = [
    { en: "plastic", vn: "Nhựa" },
    { en: "battery", vn: "Pin" },
    { en: "textile", vn: "Vải" },
    { en: "metal", vn: "Kim loại" },
    { en: "trash", vn: "Rác thải" },
    { en: "glass", vn: "Thủy tinh" },
    { en: "paper", vn: "Giấy" },
    { en: "cardboard", vn: "Hộp giấy" },
    { en: "biological", vn: "Hữu cơ" },
]

export function ClassificationFeedback({
    classificationId,
    detectedClass,
    detectedClassEn,
}: ClassificationFeedbackProps) {
    const [feedbackState, setFeedbackState] = useState<"idle" | "incorrect" | "submitted">("idle")
    const [correctClass, setCorrectClass] = useState<string>("")
    const [comment, setComment] = useState<string>("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { toast } = useToast()

    const handleCorrectClick = async () => {
        setIsSubmitting(true)
        try {
            await submitFeedback({
                classification_id: classificationId,
                is_correct: true,
                user_comment: "Phân loại chính xác",
            })

            setFeedbackState("submitted")
            toast({
                title: "Cảm ơn bạn!",
                description: "Phản hồi của bạn đã được ghi nhận",
            })
        } catch (error) {
            toast({
                title: "Lỗi",
                description: "Không thể gửi phản hồi. Vui lòng thử lại.",
                variant: "destructive",
            })
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleIncorrectClick = () => {
        setFeedbackState("incorrect")
    }

    const handleSubmitCorrection = async () => {
        if (!correctClass) {
            toast({
                title: "Thiếu thông tin",
                description: "Vui lòng chọn loại rác đúng",
                variant: "destructive",
            })
            return
        }

        setIsSubmitting(true)
        try {
            await submitFeedback({
                classification_id: classificationId,
                is_correct: false,
                correct_class: correctClass,
                user_comment: comment || undefined,
            })

            setFeedbackState("submitted")
            toast({
                title: "Cảm ơn bạn!",
                description: "Phản hồi của bạn giúp cải thiện hệ thống",
            })
        } catch (error) {
            toast({
                title: "Lỗi",
                description: "Không thể gửi phản hồi. Vui lòng thử lại.",
                variant: "destructive",
            })
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleCancel = () => {
        setFeedbackState("idle")
        setCorrectClass("")
        setComment("")
    }

    if (feedbackState === "submitted") {
        return (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-3 text-green-800">
                    <Check className="w-5 h-5" />
                    <p className="font-medium">Cảm ơn bạn đã đóng góp phản hồi!</p>
                </div>
            </div>
        )
    }

    if (feedbackState === "incorrect") {
        return (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 space-y-4">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
                    <div className="flex-1 space-y-3">
                        <p className="font-medium text-orange-900">
                            Hệ thống nhận diện sai? Hãy cho chúng tôi biết loại rác đúng:
                        </p>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">
                                Loại rác đúng là:
                            </label>
                            <Select value={correctClass} onValueChange={setCorrectClass}>
                                <SelectTrigger className="w-full bg-white">
                                    <SelectValue placeholder="Chọn loại rác đúng" />
                                </SelectTrigger>
                                <SelectContent>
                                    {WASTE_CLASSES.filter((c) => c.vn !== detectedClass).map((wasteClass) => (
                                        <SelectItem key={wasteClass.en} value={wasteClass.vn}>
                                            {wasteClass.vn}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">
                                Ghi chú (tùy chọn):
                            </label>
                            <Textarea
                                value={comment}
                                onChange={(e) => setComment(e.target.value)}
                                placeholder="Ví dụ: Đây là hộp xốp, không phải nhựa..."
                                className="min-h-[80px] bg-white"
                            />
                        </div>

                        <div className="flex gap-2">
                            <Button
                                onClick={handleSubmitCorrection}
                                disabled={isSubmitting || !correctClass}
                                className="flex-1 bg-orange-600 hover:bg-orange-700 text-white"
                            >
                                {isSubmitting ? "Đang gửi..." : "Gửi phản hồi"}
                            </Button>
                            <Button
                                onClick={handleCancel}
                                variant="outline"
                                disabled={isSubmitting}
                            >
                                Hủy
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="space-y-3">
                <p className="text-sm font-medium text-gray-700">
                    Kết quả phân loại có chính xác không?
                </p>
                <div className="flex gap-3">
                    <Button
                        onClick={handleCorrectClick}
                        disabled={isSubmitting}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    >
                        <ThumbsUp className="w-4 h-4 mr-2" />
                        Chính xác
                    </Button>
                    <Button
                        onClick={handleIncorrectClick}
                        disabled={isSubmitting}
                        variant="outline"
                        className="flex-1 border-orange-300 text-orange-700 hover:bg-orange-50"
                    >
                        <ThumbsDown className="w-4 h-4 mr-2" />
                        Không chính xác
                    </Button>
                </div>
            </div>
        </div>
    )
}
