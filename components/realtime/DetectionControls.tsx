'use client';

/**
 * DetectionControls Component
 * Start/Stop buttons for real-time detection
 */

import { Button } from '@/components/ui/button';
import { Play, Square, Loader2 } from 'lucide-react';

interface DetectionControlsProps {
  isActive: boolean;
  isLoading: boolean;
  onStart: () => void;
  onStop: () => void;
}

export const DetectionControls = ({
  isActive,
  isLoading,
  onStart,
  onStop,
}: DetectionControlsProps) => {
  return (
    <div className="flex items-center justify-center gap-4">
      {!isActive ? (
        <Button
          onClick={onStart}
          disabled={isLoading}
          size="lg"
          className="min-w-[200px]"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Đang khởi động...
            </>
          ) : (
            <>
              <Play className="mr-2 h-5 w-5" />
              Bắt đầu
            </>
          )}
        </Button>
      ) : (
        <Button
          onClick={onStop}
          variant="destructive"
          size="lg"
          className="min-w-[200px]"
        >
          <Square className="mr-2 h-5 w-5" />
          Dừng lại
        </Button>
      )}
    </div>
  );
};
