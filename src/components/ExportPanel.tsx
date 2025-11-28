import { useState } from 'react';
import type { CollageSettings, LoadedImage } from '../utils/collageEngine';
import { generateCollage, downloadCollage } from '../utils/collageEngine';

interface ExportPanelProps {
  imageGroups: LoadedImage[][];
  settings: CollageSettings;
  disabled: boolean;
}

export default function ExportPanel({ imageGroups, settings, disabled }: ExportPanelProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'png' | 'jpeg'>('png');
  const [exportProgress, setExportProgress] = useState({ current: 0, total: 0 });

  const handleExportAll = async () => {
    if (imageGroups.length === 0) return;

    setIsExporting(true);
    setExportProgress({ current: 0, total: imageGroups.length });
    
    try {
      for (let i = 0; i < imageGroups.length; i++) {
        setExportProgress({ current: i + 1, total: imageGroups.length });
        const canvas = generateCollage(imageGroups[i], settings);
        await downloadCollage(canvas, `collage_${String(i + 1).padStart(2, '0')}`, exportFormat);
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export some collages. Please try again.');
    } finally {
      setIsExporting(false);
      setExportProgress({ current: 0, total: 0 });
    }
  };

  const handleExportSingle = async (index: number) => {
    if (!imageGroups[index]) return;

    setIsExporting(true);
    try {
      const canvas = generateCollage(imageGroups[index], settings);
      await downloadCollage(canvas, `collage_${String(index + 1).padStart(2, '0')}`, exportFormat);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export collage. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-panel">
      <div className="setting-group">
        <label htmlFor="exportFormat">Format</label>
        <select
          id="exportFormat"
          value={exportFormat}
          onChange={(e) => setExportFormat(e.target.value as 'png' | 'jpeg')}
          disabled={disabled || isExporting}
        >
          <option value="png">PNG (High Quality)</option>
          <option value="jpeg">JPG (Smaller Size)</option>
        </select>
      </div>

      <div className="export-buttons">
        <button
          className="export-btn primary"
          onClick={handleExportAll}
          disabled={disabled || isExporting || imageGroups.length === 0}
        >
          {isExporting ? (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="animate-spin">
                <path d="M21 12a9 9 0 11-6.219-8.56" />
              </svg>
              Exporting {exportProgress.current}/{exportProgress.total}...
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download All ({imageGroups.length})
            </>
          )}
        </button>

        {imageGroups.length > 1 && !isExporting && (
          <div className="individual-exports">
            <p>Or download individually:</p>
            <div className="export-grid">
              {imageGroups.map((_, index) => (
                <button
                  key={index}
                  className="export-btn secondary"
                  onClick={() => handleExportSingle(index)}
                  disabled={disabled || isExporting}
                >
                  Collage {index + 1}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
