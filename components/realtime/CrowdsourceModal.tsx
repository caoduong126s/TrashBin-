'use client';

import { useState } from 'react';
import { X, Upload, Check, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { submitCrowdsourceImage } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

interface CrowdsourceModalProps {
    isOpen: boolean;
    onClose: () => void;
    capturedFrame: string | null; // Data URL
    initialClass?: string;
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
];

export const CrowdsourceModal = ({
    isOpen,
    onClose,
    capturedFrame,
    initialClass
}: CrowdsourceModalProps) => {
    const [correctClass, setCorrectClass] = useState<string>(initialClass || "");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const { toast } = useToast();

    if (!isOpen) return null;

    const handleSubmit = async () => {
        if (!correctClass || !capturedFrame) return;

        setIsSubmitting(true);
        try {
            // Convert data URL to File
            const response = await fetch(capturedFrame);
            const blob = await response.blob();
            const file = new File([blob], "crowdsource.jpg", { type: "image/jpeg" });

            await submitCrowdsourceImage(file, correctClass);

            setIsSuccess(true);
            toast({
                title: "Cảm ơn bạn!",
                description: "Hình ảnh đã được gửi để cải thiện hệ thống.",
            });

            setTimeout(() => {
                onClose();
                setIsSuccess(false);
                setCorrectClass("");
            }, 2000);
        } catch (error) {
            toast({
                title: "Lỗi",
                description: "Không thể gửi ảnh. Vui lòng thử lại.",
                variant: "destructive",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="bg-orange-600 p-4 text-white flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        <h3 className="font-bold">Báo lỗi nhận diện</h3>
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-lg transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    {/* Image Preview */}
                    <div className="relative aspect-video bg-gray-100 rounded-xl overflow-hidden border-2 border-dashed border-gray-300">
                        {capturedFrame ? (
                            <img src={capturedFrame} alt="Captured frame" className="w-full h-full object-cover" />
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-gray-400">
                                <Upload className="w-8 h-8 mb-2" />
                                <p className="text-sm">Đang tải ảnh...</p>
                            </div>
                        )}
                    </div>

                    {!isSuccess ? (
                        <>
                            <div className="space-y-4">
                                <p className="text-sm text-gray-600">
                                    Vui lòng giúp chúng tôi biết loại rác chính xác trong hình ảnh này để cải thiện trí tuệ nhân tạo.
                                </p>

                                <div className="space-y-2">
                                    <label className="text-sm font-semibold text-gray-700">Loại rác đúng là:</label>
                                    <Select value={correctClass} onValueChange={setCorrectClass}>
                                        <SelectTrigger className="w-full">
                                            <SelectValue placeholder="Chọn loại rác đúng" />
                                        </SelectTrigger>
                                        <SelectContent className="z-[110]">
                                            {WASTE_CLASSES.map((wc) => (
                                                <SelectItem key={wc.en} value={wc.vn}>
                                                    {wc.vn}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <Button
                                    variant="outline"
                                    onClick={onClose}
                                    className="flex-1"
                                    disabled={isSubmitting}
                                >
                                    Hủy
                                </Button>
                                <Button
                                    onClick={handleSubmit}
                                    className="flex-1 bg-orange-600 hover:bg-orange-700 text-white"
                                    disabled={isSubmitting || !correctClass}
                                >
                                    {isSubmitting ? "Đang gửi..." : "Gửi báo lỗi"}
                                </Button>
                            </div>
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
                            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
                                <Check className="w-8 h-8" />
                            </div>
                            <h4 className="text-xl font-bold text-gray-900">Gửi thành công!</h4>
                            <p className="text-gray-600">Phản hồi của bạn vô cùng giá trị.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
