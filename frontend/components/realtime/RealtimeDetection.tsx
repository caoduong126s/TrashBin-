'use client';

/**
 * RealtimeDetection Component
 * Main container for real-time waste detection
 * With Disposal Instructions, Hazard Warnings, and Debug Panel
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocketDetection } from '@/hooks/useWebSocketDetection';
import { useCamera } from '@/lib/cameraUtils';
import { CameraView } from './CameraView';
import { DetectionFeedback } from './DetectionFeedback';
import { DetectionControls } from './DetectionControls';
import { DisposalInstructions } from './DisposalInstructions';
import { HazardWarning } from './HazardWarning';
import { PredictionDebug } from './PredictionDebug';
import { BoundingBoxOverlay } from './BoundingBoxOverlay';
import { CrowdsourceModal } from './CrowdsourceModal';
import { toast } from '@/hooks/use-toast';

export const RealtimeDetection = () => {
  const [isActive, setIsActive] = useState(false);
  const [fps, setFps] = useState(0);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showHazardWarning, setShowHazardWarning] = useState(false);
  const [isCrowdsourceOpen, setIsCrowdsourceOpen] = useState(false);
  const [capturedFrameData, setCapturedFrameData] = useState<string | null>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastFrameTimeRef = useRef<number>(0);
  const frameCountRef = useRef<number>(0);

  // Debouncing for disposal instructions
  const [stableDetection, setStableDetection] = useState<any>(null);
  const instructionsTimerRef = useRef<NodeJS.Timeout | null>(null);
  const instructionsHideTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastDetectionRef = useRef<any>(null);

  // Camera hook
  const {
    videoRef,
    isActive: isCameraActive,
    isLoading: isCameraLoading,
    error: cameraError,
    startCamera,
    stopCamera,
    captureFrame,
  } = useCamera();

  // WebSocket hook
  const {
    isConnected,
    isConnecting,
    error: wsError,
    lastResult,
    connect: connectWS,
    disconnect: disconnectWS,
    sendFrame,
  } = useWebSocketDetection({
    autoConnect: false,
    onResult: (result) => {
      // Debounced instruction display logic
      if (result.success && result.data?.stable && result.data.detections?.[0]) {
        const primaryDetection = result.data.detections[0];
        lastDetectionRef.current = primaryDetection;

        // Clear any pending hide timer (detection is still active)
        if (instructionsHideTimerRef.current) {
          clearTimeout(instructionsHideTimerRef.current);
          instructionsHideTimerRef.current = null;
        }

        // If instructions not showing yet, delay showing by 400ms
        if (!showInstructions) {
          if (!instructionsTimerRef.current) {
            instructionsTimerRef.current = setTimeout(() => {
              setStableDetection(primaryDetection);
              setShowInstructions(true);
              instructionsTimerRef.current = null;

              // Show hazard warning for hazardous waste
              if (primaryDetection.bin_type === 'hazardous') {
                setShowHazardWarning(true);
              }
            }, 50); // Instant feedback (Backend handles debouncing)
          }
        } else {
          // Update the sticky detection data to keep UI fresh but stable
          setStableDetection(primaryDetection);
        }
      } else {
        // No stable detection - hide instructions after minimum display time
        if (showInstructions && !instructionsHideTimerRef.current) {
          // Keep visible for at least 3 seconds after last detection (Increased for stability)
          instructionsHideTimerRef.current = setTimeout(() => {
            setShowInstructions(false);
            setShowHazardWarning(false);
            setStableDetection(null);
            instructionsHideTimerRef.current = null;
          }, 3000); // 3 second minimum display time
        }

        // Clear show timer if detection disappeared before showing
        if (instructionsTimerRef.current) {
          clearTimeout(instructionsTimerRef.current);
          instructionsTimerRef.current = null;
        }
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      toast({
        title: 'Lỗi kết nối',
        description: 'Không thể kết nối đến máy chủ. Đang thử lại...',
        variant: 'destructive',
      });
    },
  });

  // Start detection
  const handleStart = useCallback(async () => {
    try {
      console.log('🚀 Starting real-time detection...');

      // Start camera
      console.log('📹 Starting camera...');
      await startCamera({
        width: 640,
        height: 480,
        facingMode: 'environment',
      });
      console.log('✅ Camera started');

      // Connect WebSocket
      console.log('🔌 Connecting WebSocket...');
      connectWS();
      console.log('⏳ WebSocket connection initiated');

      setIsActive(true);
    } catch (error) {
      console.error('❌ Failed to start detection:', error);
    }
  }, [startCamera, connectWS]);

  // Stop detection
  const handleStop = useCallback(() => {
    // Stop frame capture
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }

    // Clear debouncing timers
    if (instructionsTimerRef.current) {
      clearTimeout(instructionsTimerRef.current);
      instructionsTimerRef.current = null;
    }
    if (instructionsHideTimerRef.current) {
      clearTimeout(instructionsHideTimerRef.current);
      instructionsHideTimerRef.current = null;
    }

    // Stop camera
    stopCamera();

    // Disconnect WebSocket
    disconnectWS();

    setIsActive(false);
    setFps(0);
    setShowInstructions(false);
    setShowHazardWarning(false);
    setIsCrowdsourceOpen(false);
  }, [stopCamera, disconnectWS]);

  // Handle reporting detection error
  const handleReportError = useCallback(() => {
    // Capture current frame at high quality for crowdsourcing
    const frame = captureFrame(0.9);
    if (frame) {
      setCapturedFrameData(frame);
      setIsCrowdsourceOpen(true);
      // Pause instructions hide timer so modal can stay open
      if (instructionsHideTimerRef.current) {
        clearTimeout(instructionsHideTimerRef.current);
        instructionsHideTimerRef.current = null;
      }
    }
  }, [captureFrame]);

  // Capture and send frames
  useEffect(() => {
    if (!isActive || !isCameraActive || !isConnected) {
      return;
    }

    // Send frames at ~10 FPS (100ms interval)
    // Optimization: Reduced from ~5 FPS (200ms) but we will send smaller optimized frames
    const interval = setInterval(() => {
      // Optimization: Resize to 640x480 (in cameraUtils update) and use 0.5 quality
      const frame = captureFrame(0.5);

      if (frame) {
        const sent = sendFrame(frame);

        if (sent) {
          // Calculate FPS
          const now = Date.now();
          if (lastFrameTimeRef.current > 0) {
            const delta = now - lastFrameTimeRef.current;
            const currentFps = 1000 / delta;
            setFps(currentFps);
          }
          lastFrameTimeRef.current = now;
          frameCountRef.current++;
        }
      }
    }, 100); // 10 FPS (100ms)

    frameIntervalRef.current = interval;

    return () => {
      clearInterval(interval);
    };
  }, [isActive, isCameraActive, isConnected, captureFrame, sendFrame]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      handleStop();
    };
  }, [handleStop]);

  // Combined error state
  const error = cameraError || wsError;

  return (
    <div className="flex flex-col gap-4 w-full max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Phát hiện Real-time</h2>

        {/* Status indicators */}
        <div className="flex gap-2 text-sm">
          <div className={`flex items-center gap-1 ${isCameraActive ? 'text-green-600' : 'text-gray-400'}`}>
            <div className={`w-2 h-2 rounded-full ${isCameraActive ? 'bg-green-600' : 'bg-gray-400'}`} />
            Camera
          </div>
          <div className={`flex items-center gap-1 ${isConnected ? 'text-green-600' : 'text-gray-400'}`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600' : 'bg-gray-400'}`} />
            WebSocket
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          <p className="font-semibold">Lỗi:</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Camera view with overlay */}
      <div className="relative">
        <CameraView
          videoRef={videoRef}
          isActive={isCameraActive}
          isLoading={isCameraLoading}
        />

        {isActive && (
          <>
            {/* Bounding Box Overlay */}
            <BoundingBoxOverlay
              detections={lastResult?.data?.detections}
              videoRef={videoRef}
            />

            <DetectionFeedback
              result={lastResult}
              fps={fps}
              isProcessing={isConnected}
            />
          </>
        )}
      </div>

      {/* Controls */}
      <DetectionControls
        isActive={isActive}
        isLoading={isCameraLoading || isConnecting}
        onStart={handleStart}
        onStop={handleStop}
      />

      {/* Info */}
      {!isActive && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-blue-800">
          <p className="font-semibold mb-2">Hướng dẫn:</p>
          <ul className="text-sm space-y-1 list-disc list-inside">
            <li>Nhấn "Bắt đầu" để khởi động camera và kết nối</li>
            <li>Đưa vật phẩm rác vào khung hình</li>
            <li>Đợi khoảng 1 giây để kết quả ổn định</li>
            <li>Đảm bảo ánh sáng tốt và background đơn giản</li>
          </ul>
        </div>
      )}

      {/* Disposal Instructions */}
      {isActive && showInstructions && stableDetection && (
        <DisposalInstructions
          key={stableDetection.class_name}
          className={stableDetection.class_name}
          binType={stableDetection.bin_type}
          confidence={stableDetection.confidence}
          onClose={() => {
            setShowInstructions(false);
            setStableDetection(null);
          }}
          onReportError={handleReportError}
        />
      )}

      {/* Hazard Warning */}
      {isActive && showHazardWarning && stableDetection && (
        <HazardWarning
          className={stableDetection.class_name}
          confidence={stableDetection.confidence}
          onDismiss={() => setShowHazardWarning(false)}
        />
      )}

      {/* Debug Predictions */}
      {isActive && lastResult?.success && lastResult.debug && (
        <PredictionDebug
          predictions={lastResult.debug.all_predictions}
          topClass={lastResult.data?.detections?.[0]?.class_name}
          usedSecondChoice={(lastResult.data as any)?.used_second_choice}
        />
      )}

      {/* Crowdsource Modal */}
      <CrowdsourceModal
        isOpen={isCrowdsourceOpen}
        onClose={() => setIsCrowdsourceOpen(false)}
        capturedFrame={capturedFrameData}
        initialClass={stableDetection?.class_name}
      />
    </div>
  );
};