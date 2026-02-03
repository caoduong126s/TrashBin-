/**
 * useWebSocketDetection Hook
 * Manages WebSocket connection for real-time waste detection
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface DetectionResult {
  success: boolean;
  data?: {
    detections: Array<{
      box: number[];
      confidence: number;
      class_name: string;
      class_name_en: string;
      bin_type: 'recyclable' | 'hazardous' | 'general' | 'organic';
      detection_id: number;
    }>;
    total_objects: number;
    stable: boolean;
    // Potentially other fields
    processing_time?: number;
    preprocessing?: {
      is_low_light: boolean;
      method: string;
      enhancement_applied: boolean;
    };
  };
  metadata?: {
    fps: number;
    processing_time_ms: number;
    frame_count: number;
    inference_count: number;
    inference_ratio: number;
  };
  debug?: {
    all_predictions: Record<string, number>;
  };
  error?: string;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastResult: DetectionResult | null;
}

interface UseWebSocketDetectionProps {
  url?: string;
  autoConnect?: boolean;
  onResult?: (result: DetectionResult) => void;
  onError?: (error: Error) => void;
}

export const useWebSocketDetection = ({
  url = 'ws://localhost:8000/api/v1/ws/realtime-detect',
  autoConnect = false,
  onResult,
  onError,
}: UseWebSocketDetectionProps = {}) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectCountRef = useRef<number>(0);
  // Ref to hold the connect function to break circular dependency
  const connectRef = useRef<() => void>(() => { });

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastResult: null,
  });

  // Reconnection logic
  const scheduleReconnect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    // Exponential backoff
    const delay = Math.min(1000 * Math.pow(2, reconnectCountRef.current), 10000);
    console.log(`🔄 Reconnecting in ${delay}ms (Attempt ${reconnectCountRef.current + 1})...`);

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectCountRef.current += 1;
      // Use ref to call connect
      if (connectRef.current) {
        connectRef.current();
      }
    }, delay);
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    console.log('🔌 Attempting WebSocket connection to:', url);
    setState((prev) => ({ ...prev, isConnecting: true, error: null }));

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('✅ WebSocket connected successfully!');
        setState((prev) => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          error: null,
        }));
        reconnectCountRef.current = 0; // Reset backoff
      };

      ws.onmessage = (event) => {
        try {
          const result: DetectionResult = JSON.parse(event.data);
          setState((prev) => ({ ...prev, lastResult: result }));
          if (onResult) onResult(result);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (event) => {
        console.error('❌ WebSocket error:', event);
        const error = new Error('WebSocket connection error');
        setState((prev) => ({
          ...prev,
          error: error.message,
          isConnecting: false,
        }));
        if (onError) onError(error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setState((prev) => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));

        // Reconnect if not clean close or connection lost
        if (!event.wasClean && event.code !== 1000) {
          scheduleReconnect();
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setState((prev) => ({
        ...prev,
        error: (error as Error).message,
        isConnecting: false,
      }));
      scheduleReconnect();
    }
  }, [url, onResult, onError, scheduleReconnect]);

  // Update ref whenever connect changes
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      lastResult: null,
    });
  }, []);

  // Send frame to backend
  const sendFrame = useCallback(
    (frameData: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        // console.warn('WebSocket not connected');
        return false;
      }

      try {
        wsRef.current.send(frameData);
        return true;
      } catch (error) {
        console.error('Failed to send frame:', error);
        return false;
      }
    },
    []
  );

  // Auto-connect and Visibility Handler
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Handle visibility change
    const handleVisibilityChange = () => {
      if (document.hidden) {
        console.log('🙈 Tab hidden, pausing WebSocket...');
        if (wsRef.current) {
          wsRef.current.close(1000, 'Tab hidden');
        }
      } else {
        console.log('👀 Tab visible, resuming WebSocket...');
        // We only auto-reconnect if it was previously connected or autoConnect is true
        // But since we lost state on close, we can check logic or just rely on autoConnect.
        // Or if we want to be sticky, we could track 'wasConnected'.
        // For now, let's just reconnect if autoConnect is true.
        // Ideally we should track desired state.
        if (autoConnect) {
          connect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps to run once

  return {
    ...state,
    connect,
    disconnect,
    sendFrame,
  };
};