'use client';

import { useEffect, useRef } from 'react';

interface BoundingBoxOverlayProps {
    detections: Array<{
        box: number[];
        class_name: string;
        confidence: number;
        bin_type: string;
    }> | undefined;
    videoRef: React.RefObject<HTMLVideoElement | null>;
}

const BIN_COLORS: Record<string, string> = {
    recyclable: '#22c55e', // green-500
    hazardous: '#ef4444', // red-500
    general: '#6b7280',    // gray-500
    organic: '#f97316',    // orange-500
};

export const BoundingBoxOverlay = ({ detections, videoRef }: BoundingBoxOverlayProps) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const video = videoRef.current;
        if (!canvas || !video) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Use requestAnimationFrame for smoother rendering
        const render = () => {
            // Match canvas size to displayed video size
            canvas.width = video.clientWidth;
            canvas.height = video.clientHeight;

            // Clear previous drawings with slight fade for smoother transitions
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!detections || detections.length === 0) return;

            // Calculate scaling factors
            const scaleX = canvas.width / 640;
            const scaleY = canvas.height / 480;

            detections.forEach((det) => {
                const [x1, y1, x2, y2] = det.box;
                const color = BIN_COLORS[det.bin_type] || BIN_COLORS.general;

                // Scale coordinates
                const scaledX = x1 * scaleX;
                const scaledY = y1 * scaleY;
                const scaledW = (x2 - x1) * scaleX;
                const scaledH = (y2 - y1) * scaleY;

                // Draw Box with shadow for better visibility
                ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
                ctx.shadowBlur = 4;
                ctx.strokeStyle = color;
                ctx.lineWidth = 3;
                ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);
                ctx.shadowBlur = 0;

                // Draw Background for Label
                ctx.fillStyle = color;
                const text = `${det.class_name} ${Math.round(det.confidence)}%`;
                const font = 'bold 14px "Inter", sans-serif';
                ctx.font = font;
                const textMetrics = ctx.measureText(text);
                const padding = 4;

                ctx.fillRect(
                    scaledX,
                    scaledY - 24,
                    textMetrics.width + padding * 2,
                    24
                );

                // Draw Label
                ctx.fillStyle = '#ffffff';
                ctx.fillText(text, scaledX + padding, scaledY - 7);
            });
        };

        const animationFrame = requestAnimationFrame(render);
        return () => cancelAnimationFrame(animationFrame);

    }, [detections, videoRef?.current?.clientWidth, videoRef?.current?.clientHeight]);
    // Depend on client dimensions to redraw on resize

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 pointer-events-none"
        />
    );
};
