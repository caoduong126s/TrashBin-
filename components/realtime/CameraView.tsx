'use client';

/**
 * CameraView Component
 * Displays video feed from camera with visual guides
 */

import { Loader2, Camera } from 'lucide-react';

interface CameraViewProps {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  isActive: boolean;
  isLoading: boolean;
}

export const CameraView = ({ videoRef, isActive, isLoading }: CameraViewProps) => {
  return (
    <div className="relative w-full aspect-video bg-gray-900 rounded-xl overflow-hidden">
      {/* Video element */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
      />

      {/* Loading state */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
          <div className="text-center text-white">
            <Loader2 className="w-12 h-12 animate-spin mx-auto mb-2" />
            <p className="text-sm">Đang khởi động camera...</p>
          </div>
        </div>
      )}

      {/* Inactive state */}
      {!isActive && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
          <div className="text-center text-white">
            <Camera className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-semibold mb-2">Camera chưa khởi động</p>
            <p className="text-sm opacity-75">Nhấn "Bắt đầu" để kích hoạt</p>
          </div>
        </div>
      )}

      {/* Guide overlay when active */}
      {isActive && !isLoading && (
        <div className="absolute inset-0 pointer-events-none">
          {/* Guide box */}
          <div className="absolute inset-8 border-4 border-green-500 rounded-lg">
            {/* Corner markers */}
            <div className="absolute -top-1 -left-1 w-8 h-8 border-t-4 border-l-4 border-green-400" />
            <div className="absolute -top-1 -right-1 w-8 h-8 border-t-4 border-r-4 border-green-400" />
            <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-4 border-l-4 border-green-400" />
            <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-4 border-r-4 border-green-400" />
          </div>

          {/* Instruction text */}
          <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/60 px-4 py-2 rounded-full">
            <p className="text-white text-sm font-medium">
              Đặt vật phẩm trong khung xanh
            </p>
          </div>
        </div>
      )}
    </div>
  );
};