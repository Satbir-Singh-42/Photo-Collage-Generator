import { useEffect, useRef, useState, useMemo } from 'react';
import type { CollageSettings, LoadedImage } from '../utils/collageEngine';
import { generateCollage, calculateGrid } from '../utils/collageEngine';

interface CollagePreviewProps {
  images: LoadedImage[];
  settings: CollageSettings;
  collageIndex: number;
}

export default function CollagePreview({ images, settings, collageIndex }: CollagePreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const settingsKey = useMemo(() => JSON.stringify({
    canvasWidth: settings.canvasWidth,
    canvasHeight: settings.canvasHeight,
    backgroundColor: settings.backgroundColor,
    outerFrameThickness: settings.outerFrameThickness,
    innerSpacing: settings.innerSpacing,
    roundedCornersRadius: settings.roundedCornersRadius,
    enableRoundedCorners: settings.enableRoundedCorners,
    enableDropShadow: settings.enableDropShadow,
    shadowBlur: settings.shadowBlur,
    shape: settings.shape,
  }), [settings.canvasWidth, settings.canvasHeight, settings.backgroundColor,
      settings.outerFrameThickness, settings.innerSpacing, settings.roundedCornersRadius,
      settings.enableRoundedCorners, settings.enableDropShadow, settings.shadowBlur, settings.shape]);

  const imageIds = useMemo(() => 
    images.map(img => img.file.name + img.file.size).join(','),
    [images]
  );

  useEffect(() => {
    if (images.length === 0) {
      setPreviewUrl(null);
      return;
    }

    let cancelled = false;
    setIsGenerating(true);

    const generatePreview = () => {
      if (cancelled) return;
      
      try {
        const canvas = generateCollage(images, settings);
        
        if (cancelled) return;
        
        const previewCanvas = document.createElement('canvas');
        const maxPreviewSize = 800;
        const scale = Math.min(maxPreviewSize / canvas.width, maxPreviewSize / canvas.height, 1);
        previewCanvas.width = canvas.width * scale;
        previewCanvas.height = canvas.height * scale;
        
        const ctx = previewCanvas.getContext('2d')!;
        ctx.drawImage(canvas, 0, 0, previewCanvas.width, previewCanvas.height);
        
        const url = previewCanvas.toDataURL('image/jpeg', 0.8);
        
        if (!cancelled) {
          setPreviewUrl(url);
          setIsGenerating(false);
        }
      } catch (error) {
        console.error('Failed to generate collage:', error);
        if (!cancelled) {
          setIsGenerating(false);
        }
      }
    };

    const timeoutId = setTimeout(generatePreview, 200);
    return () => {
      cancelled = true;
      clearTimeout(timeoutId);
    };
  }, [imageIds, settingsKey]);

  const { rows, cols } = calculateGrid(images.length);

  return (
    <div className="collage-preview" ref={containerRef}>
      {images.length === 0 ? (
        <div className="preview-placeholder">
          <p>Upload images to see preview</p>
        </div>
      ) : isGenerating ? (
        <div className="preview-loading">
          <div className="spinner"></div>
          <p>Generating collage...</p>
        </div>
      ) : previewUrl ? (
        <div className="preview-image-container">
          <div className="preview-info">
            Collage {collageIndex + 1}: {images.length} images in {rows}x{cols} grid
          </div>
          <img src={previewUrl} alt={`Collage preview ${collageIndex + 1}`} className="preview-image" />
        </div>
      ) : null}
    </div>
  );
}
