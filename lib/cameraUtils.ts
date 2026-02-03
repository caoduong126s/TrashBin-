/**
 * Camera utilities for real-time detection
 */

export interface CameraConstraints {
  width?: number;
  height?: number;
  facingMode?: 'user' | 'environment';
  frameRate?: number;
}

export class CameraManager {
  private stream: MediaStream | null = null;
  private videoElement: HTMLVideoElement | null = null;

  /**
   * Request camera access
   */
  async requestCamera(
    constraints: CameraConstraints = {}
  ): Promise<MediaStream> {
    try {
      const defaultConstraints: MediaStreamConstraints = {
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'environment', // Back camera on mobile
          frameRate: { ideal: 30, max: 30 },
          ...constraints,
        },
        audio: false,
      };

      this.stream = await navigator.mediaDevices.getUserMedia(
        defaultConstraints
      );

      console.log('✅ Camera access granted');
      return this.stream;
    } catch (error) {
      console.error('❌ Camera access denied:', error);
      throw new Error('Could not access camera. Please grant permission.');
    }
  }

  /**
   * Attach stream to video element
   */
  attachToVideo(videoElement: HTMLVideoElement): void {
    if (!this.stream) {
      throw new Error('No camera stream available');
    }

    videoElement.srcObject = this.stream;
    this.videoElement = videoElement;
  }

  /**
   * Capture frame from video element
   */
  /**
   * Capture frame from video element
   * Resizes image to specified dimensions (default 640x480)
   */
  captureFrame(
    videoElement?: HTMLVideoElement,
    quality: number = 0.5,
    targetWidth: number = 640,
    targetHeight: number = 480
  ): string | null {
    const video = videoElement || this.videoElement;

    if (!video) {
      console.error('No video element available');
      return null;
    }

    try {
      // Create canvas with fixed target dimensions
      const canvas = document.createElement('canvas');
      canvas.width = targetWidth;
      canvas.height = targetHeight;

      // Draw video frame to canvas (scaled)
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        throw new Error('Could not get canvas context');
      }

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to base64 JPEG
      const base64Data = canvas.toDataURL('image/jpeg', quality);

      // Remove data URL prefix if present
      return base64Data.split(',')[1] || base64Data;
    } catch (error) {
      console.error('Failed to capture frame:', error);
      return null;
    }
  }

  /**
   * Stop camera stream
   */
  stopCamera(): void {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }

    if (this.videoElement) {
      this.videoElement.srcObject = null;
      this.videoElement = null;
    }

    console.log('📹 Camera stopped');
  }

  /**
   * Check if camera is available
   */
  static async isCameraAvailable(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some((device) => device.kind === 'videoinput');
    } catch {
      return false;
    }
  }

  /**
   * Get available cameras
   */
  static async getCameras(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter((device) => device.kind === 'videoinput');
    } catch (error) {
      console.error('Failed to get cameras:', error);
      return [];
    }
  }
}

/**
 * Hook for camera management
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export const useCamera = () => {
  const cameraManagerRef = useRef<CameraManager | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize camera manager
  useEffect(() => {
    cameraManagerRef.current = new CameraManager();

    return () => {
      if (cameraManagerRef.current) {
        cameraManagerRef.current.stopCamera();
      }
    };
  }, []);

  // Start camera
  const startCamera = useCallback(
    async (constraints?: CameraConstraints) => {
      if (!cameraManagerRef.current) return;

      setIsLoading(true);
      setError(null);

      try {
        const stream = await cameraManagerRef.current.requestCamera(
          constraints
        );

        if (videoRef.current) {
          cameraManagerRef.current.attachToVideo(videoRef.current);
          await videoRef.current.play();
        }

        setIsActive(true);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to start camera';
        setError(errorMessage);
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Stop camera
  const stopCamera = useCallback(() => {
    if (cameraManagerRef.current) {
      cameraManagerRef.current.stopCamera();
      setIsActive(false);
    }
  }, []);

  // Capture frame
  const captureFrame = useCallback((
    quality?: number,
    targetWidth?: number,
    targetHeight?: number
  ): string | null => {
    if (!cameraManagerRef.current || !videoRef.current) {
      return null;
    }
    return cameraManagerRef.current.captureFrame(
      videoRef.current,
      quality,
      targetWidth,
      targetHeight
    );
  }, []);

  return {
    videoRef,
    isActive,
    isLoading,
    error,
    startCamera,
    stopCamera,
    captureFrame,
  };
};
