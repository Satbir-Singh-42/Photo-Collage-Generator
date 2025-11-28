export type CollageShape = 'square' | 'rectangle' | 'circle' | 'heart' | 'star' | 'diamond' | 'hexagon' | 'triangle';

export interface CollageSettings {
  canvasWidth: number;
  canvasHeight: number;
  backgroundColor: string;
  transparentBackground: boolean;
  outerFrameThickness: number;
  innerSpacing: number;
  roundedCornersRadius: number;
  enableRoundedCorners: boolean;
  enableDropShadow: boolean;
  shadowOffsetX: number;
  shadowOffsetY: number;
  shadowBlur: number;
  shadowColor: string;
  imagesPerCollage: number;
  shape: CollageShape;
}

export const defaultSettings: CollageSettings = {
  canvasWidth: 3000,
  canvasHeight: 3000,
  backgroundColor: '#ffffff',
  transparentBackground: false,
  outerFrameThickness: 0,
  innerSpacing: 0,
  roundedCornersRadius: 0,
  enableRoundedCorners: false,
  enableDropShadow: false,
  shadowOffsetX: 5,
  shadowOffsetY: 5,
  shadowBlur: 0,
  shadowColor: 'rgba(0, 0, 0, 0.3)',
  imagesPerCollage: 50,
  shape: 'square',
};

export interface LoadedImage {
  file: File;
  element: HTMLImageElement;
  width: number;
  height: number;
}

export function calculateGrid(numImages: number): { rows: number; cols: number } {
  if (numImages <= 0) return { rows: 0, cols: 0 };
  
  if (numImages === 1) return { rows: 1, cols: 1 };
  if (numImages === 2) return { rows: 1, cols: 2 };
  if (numImages === 3) return { rows: 1, cols: 3 };
  if (numImages === 4) return { rows: 1, cols: 4 };
  if (numImages === 5) return { rows: 1, cols: 5 };
  if (numImages === 6) return { rows: 2, cols: 3 };
  if (numImages === 7) return { rows: 2, cols: 4 };
  if (numImages === 8) return { rows: 2, cols: 4 };
  if (numImages === 9) return { rows: 3, cols: 3 };
  if (numImages === 10) return { rows: 2, cols: 5 };
  if (numImages <= 12) return { rows: 3, cols: 4 };
  if (numImages <= 15) return { rows: 3, cols: 5 };
  if (numImages <= 20) return { rows: 4, cols: 5 };
  if (numImages <= 25) return { rows: 5, cols: 5 };
  if (numImages <= 30) return { rows: 5, cols: 6 };
  if (numImages <= 36) return { rows: 6, cols: 6 };
  if (numImages <= 42) return { rows: 6, cols: 7 };
  if (numImages <= 49) return { rows: 7, cols: 7 };
  if (numImages <= 56) return { rows: 7, cols: 8 };
  if (numImages <= 64) return { rows: 8, cols: 8 };
  if (numImages <= 72) return { rows: 8, cols: 9 };
  if (numImages <= 81) return { rows: 9, cols: 9 };
  if (numImages <= 100) return { rows: 10, cols: 10 };
  
  const cols = Math.ceil(Math.sqrt(numImages));
  let rows = Math.ceil(numImages / cols);
  
  while (rows * cols < numImages) {
    rows++;
  }
  
  return { rows, cols };
}

export function splitIntoGroups<T>(items: T[], groupSize: number): T[][] {
  const groups: T[][] = [];
  for (let i = 0; i < items.length; i += groupSize) {
    groups.push(items.slice(i, i + groupSize));
  }
  return groups;
}

export async function loadImage(file: File): Promise<LoadedImage> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        resolve({
          file,
          element: img,
          width: img.width,
          height: img.height,
        });
      };
      img.onerror = () => reject(new Error(`Failed to load image: ${file.name}`));
      img.src = e.target?.result as string;
    };
    reader.onerror = () => reject(new Error(`Failed to read file: ${file.name}`));
    reader.readAsDataURL(file);
  });
}

export async function loadImages(
  files: File[],
  onProgress?: (loaded: number, total: number) => void
): Promise<LoadedImage[]> {
  const images: LoadedImage[] = [];
  let loaded = 0;
  
  for (const file of files) {
    try {
      const img = await loadImage(file);
      images.push(img);
    } catch (error) {
      console.warn(`Skipping corrupted/unreadable image: ${file.name}`, error);
    }
    loaded++;
    onProgress?.(loaded, files.length);
  }
  
  return images;
}

function fitImage(
  img: HTMLImageElement,
  targetWidth: number,
  targetHeight: number,
  backgroundColor: string
): HTMLCanvasElement {
  const imgRatio = img.width / img.height;
  const targetRatio = targetWidth / targetHeight;
  
  let drawWidth: number;
  let drawHeight: number;
  let drawX: number;
  let drawY: number;
  
  if (imgRatio > targetRatio) {
    drawWidth = targetWidth;
    drawHeight = targetWidth / imgRatio;
    drawX = 0;
    drawY = (targetHeight - drawHeight) / 2;
  } else {
    drawHeight = targetHeight;
    drawWidth = targetHeight * imgRatio;
    drawX = (targetWidth - drawWidth) / 2;
    drawY = 0;
  }
  
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = targetWidth;
  tempCanvas.height = targetHeight;
  const tempCtx = tempCanvas.getContext('2d')!;
  
  if (backgroundColor !== 'transparent') {
    tempCtx.fillStyle = backgroundColor;
    tempCtx.fillRect(0, 0, targetWidth, targetHeight);
  }
  
  tempCtx.drawImage(
    img,
    0, 0, img.width, img.height,
    drawX, drawY, drawWidth, drawHeight
  );
  
  return tempCanvas;
}

function drawRoundedRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
): void {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function drawHeartPath(ctx: CanvasRenderingContext2D, centerX: number, centerY: number, size: number): void {
  ctx.beginPath();
  const scale = size / 32;
  
  for (let i = 0; i <= 360; i++) {
    const t = (i * Math.PI) / 180;
    const x = 16 * Math.pow(Math.sin(t), 3);
    const y = -(13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t));
    
    const px = centerX + x * scale;
    const py = centerY + y * scale;
    
    if (i === 0) {
      ctx.moveTo(px, py);
    } else {
      ctx.lineTo(px, py);
    }
  }
  ctx.closePath();
}

function drawStarPath(ctx: CanvasRenderingContext2D, centerX: number, centerY: number, size: number): void {
  ctx.beginPath();
  const outerRadius = size / 2;
  const innerRadius = outerRadius * 0.4;
  const points = 5;
  
  for (let i = 0; i < points * 2; i++) {
    const radius = i % 2 === 0 ? outerRadius : innerRadius;
    const angle = (i * Math.PI) / points - Math.PI / 2;
    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius;
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.closePath();
}

function drawDiamondPath(ctx: CanvasRenderingContext2D, centerX: number, centerY: number, size: number): void {
  ctx.beginPath();
  const halfSize = size / 2;
  ctx.moveTo(centerX, centerY - halfSize);
  ctx.lineTo(centerX + halfSize, centerY);
  ctx.lineTo(centerX, centerY + halfSize);
  ctx.lineTo(centerX - halfSize, centerY);
  ctx.closePath();
}

function drawHexagonPath(ctx: CanvasRenderingContext2D, centerX: number, centerY: number, size: number): void {
  ctx.beginPath();
  const radius = size / 2;
  
  for (let i = 0; i < 6; i++) {
    const angle = (i * Math.PI) / 3 - Math.PI / 2;
    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius;
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.closePath();
}

function drawTrianglePath(ctx: CanvasRenderingContext2D, centerX: number, centerY: number, size: number): void {
  ctx.beginPath();
  const height = size * 0.866;
  const halfWidth = size / 2;
  
  ctx.moveTo(centerX, centerY - height / 2);
  ctx.lineTo(centerX + halfWidth, centerY + height / 2);
  ctx.lineTo(centerX - halfWidth, centerY + height / 2);
  ctx.closePath();
}

function applyShapeMask(
  canvas: HTMLCanvasElement,
  shape: CollageShape
): HTMLCanvasElement {
  if (shape === 'square' || shape === 'rectangle') {
    return canvas;
  }
  
  const maskedCanvas = document.createElement('canvas');
  maskedCanvas.width = canvas.width;
  maskedCanvas.height = canvas.height;
  const ctx = maskedCanvas.getContext('2d')!;
  
  ctx.save();
  
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const size = Math.min(canvas.width, canvas.height) * 0.95;
  
  if (shape === 'circle') {
    const radius = Math.min(canvas.width, canvas.height) / 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.closePath();
  } else if (shape === 'heart') {
    const heartCenterY = canvas.height * 0.45;
    const heartSize = Math.min(canvas.width, canvas.height) * 0.9;
    drawHeartPath(ctx, centerX, heartCenterY, heartSize);
  } else if (shape === 'star') {
    drawStarPath(ctx, centerX, centerY, size);
  } else if (shape === 'diamond') {
    drawDiamondPath(ctx, centerX, centerY, size);
  } else if (shape === 'hexagon') {
    drawHexagonPath(ctx, centerX, centerY, size);
  } else if (shape === 'triangle') {
    drawTrianglePath(ctx, centerX, centerY, size);
  }
  
  ctx.clip();
  ctx.drawImage(canvas, 0, 0);
  ctx.restore();
  
  return maskedCanvas;
}

export function generateCollage(
  images: LoadedImage[],
  settings: CollageSettings
): HTMLCanvasElement {
  const { rows, cols } = calculateGrid(images.length);
  
  const canvas = document.createElement('canvas');
  canvas.width = settings.canvasWidth;
  canvas.height = settings.canvasHeight;
  const ctx = canvas.getContext('2d')!;
  
  if (!settings.transparentBackground) {
    ctx.fillStyle = settings.backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  
  const frame = settings.outerFrameThickness;
  const spacing = settings.innerSpacing;
  
  const totalHSpacing = (cols - 1) * spacing;
  const totalVSpacing = (rows - 1) * spacing;
  const usableW = settings.canvasWidth - 2 * frame - totalHSpacing;
  const usableH = settings.canvasHeight - 2 * frame - totalVSpacing;
  
  const cellW = Math.floor(usableW / cols);
  const cellH = Math.floor(usableH / rows);
  
  let shadowPadding = 0;
  if (settings.enableDropShadow) {
    shadowPadding = settings.shadowBlur + Math.max(
      Math.abs(settings.shadowOffsetX),
      Math.abs(settings.shadowOffsetY)
    );
  }
  
  const extraMargin = 4;
  let imgW = cellW - 2 * shadowPadding - extraMargin;
  let imgH = cellH - 2 * shadowPadding - extraMargin;
  
  const minSize = 20;
  if (imgW < minSize || imgH < minSize) {
    imgW = Math.max(minSize, cellW - 10);
    imgH = Math.max(minSize, cellH - 10);
    shadowPadding = 2;
  }
  
  const totalImages = images.length;
  const lastRowImageCount = totalImages % cols || cols;
  const lastRowIndex = rows - 1;
  
  for (let idx = 0; idx < images.length; idx++) {
    const row = Math.floor(idx / cols);
    const col = idx % cols;
    
    let rowOffset = 0;
    if (row === lastRowIndex && lastRowImageCount < cols) {
      const emptySpaces = cols - lastRowImageCount;
      rowOffset = (emptySpaces * (cellW + spacing)) / 2;
    }
    
    const cellX = frame + col * (cellW + spacing) + rowOffset;
    const cellY = frame + row * (cellH + spacing);
    
    const img = images[idx].element;
    
    const bgColor = settings.transparentBackground ? 'transparent' : settings.backgroundColor;
    let processedCanvas = fitImage(img, imgW, imgH, bgColor);
    
    if (settings.enableRoundedCorners && settings.roundedCornersRadius > 0) {
      const roundedCanvas = document.createElement('canvas');
      roundedCanvas.width = imgW;
      roundedCanvas.height = imgH;
      const roundedCtx = roundedCanvas.getContext('2d')!;
      
      roundedCtx.save();
      drawRoundedRect(roundedCtx, 0, 0, imgW, imgH, settings.roundedCornersRadius);
      roundedCtx.clip();
      roundedCtx.drawImage(processedCanvas, 0, 0);
      roundedCtx.restore();
      
      processedCanvas = roundedCanvas;
    }
    
    let finalW = imgW;
    let finalH = imgH;
    
    if (settings.enableDropShadow) {
      ctx.save();
      ctx.shadowColor = settings.shadowColor;
      ctx.shadowBlur = settings.shadowBlur;
      ctx.shadowOffsetX = settings.shadowOffsetX;
      ctx.shadowOffsetY = settings.shadowOffsetY;
    }
    
    const x = cellX + Math.floor((cellW - finalW) / 2);
    const y = cellY + Math.floor((cellH - finalH) / 2);
    
    if (settings.enableDropShadow && settings.enableRoundedCorners) {
      ctx.fillStyle = '#ffffff';
      drawRoundedRect(ctx, x, y, finalW, finalH, settings.roundedCornersRadius);
      ctx.fill();
    }
    
    ctx.drawImage(processedCanvas, x, y);
    
    if (settings.enableDropShadow) {
      ctx.restore();
    }
  }
  
  if (settings.shape !== 'square' && settings.shape !== 'rectangle') {
    return applyShapeMask(canvas, settings.shape);
  }
  
  return canvas;
}

export function canvasToBlob(canvas: HTMLCanvasElement, type: 'png' | 'jpeg', quality = 0.95): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to convert canvas to blob'));
        }
      },
      `image/${type}`,
      quality
    );
  });
}

export async function downloadCollage(
  canvas: HTMLCanvasElement,
  filename: string,
  format: 'png' | 'jpeg'
): Promise<void> {
  const blob = await canvasToBlob(canvas, format);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.${format === 'jpeg' ? 'jpg' : 'png'}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
