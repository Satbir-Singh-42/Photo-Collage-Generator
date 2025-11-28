import { useState, useRef } from 'react';
import type { LoadedImage } from '../utils/collageEngine';

interface ImageGridProps {
  images: LoadedImage[];
  onReorder: (images: LoadedImage[]) => void;
  onRotate: (index: number, rotation: number) => void;
}

export default function ImageGrid({ images, onReorder, onRotate }: ImageGridProps) {
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const dragNode = useRef<HTMLDivElement | null>(null);

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    setDragIndex(index);
    dragNode.current = e.target as HTMLDivElement;
    e.dataTransfer.effectAllowed = 'move';
    setTimeout(() => {
      if (dragNode.current) {
        dragNode.current.classList.add('dragging');
      }
    }, 0);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault();
    if (dragIndex !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleDragEnd = () => {
    if (dragIndex !== null && dragOverIndex !== null && dragIndex !== dragOverIndex) {
      const newImages = [...images];
      const [draggedImage] = newImages.splice(dragIndex, 1);
      newImages.splice(dragOverIndex, 0, draggedImage);
      onReorder(newImages);
    }
    if (dragNode.current) {
      dragNode.current.classList.remove('dragging');
    }
    setDragIndex(null);
    setDragOverIndex(null);
    dragNode.current = null;
  };

  const handleRotate = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    const currentRotation = images[index].rotation || 0;
    const newRotation = (currentRotation + 90) % 360;
    onRotate(index, newRotation);
  };

  const handleRemove = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    const newImages = images.filter((_, i) => i !== index);
    onReorder(newImages);
  };

  if (images.length === 0) return null;

  return (
    <div className="image-grid">
      <div className="image-grid-header">
        <span>Drag to reorder</span>
      </div>
      <div className="image-grid-container">
        {images.map((image, index) => (
          <div
            key={`${image.file.name}-${index}`}
            className={`image-grid-item ${dragIndex === index ? 'dragging' : ''} ${dragOverIndex === index ? 'drag-over' : ''}`}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragEnter={(e) => handleDragEnter(e, index)}
            onDragOver={handleDragOver}
            onDragEnd={handleDragEnd}
          >
            <div className="image-grid-thumbnail" style={{ transform: `rotate(${image.rotation || 0}deg)` }}>
              <img src={image.element.src} alt={image.file.name} />
            </div>
            <div className="image-grid-controls">
              <button
                className="image-control-btn rotate-btn"
                onClick={(e) => handleRotate(index, e)}
                title="Rotate 90°"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 4v6h-6" />
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
                </svg>
              </button>
              <button
                className="image-control-btn remove-btn"
                onClick={(e) => handleRemove(index, e)}
                title="Remove"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div className="image-grid-index">{index + 1}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
