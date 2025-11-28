import { useState, useCallback, useMemo } from 'react';
import ImageUploader from './components/ImageUploader';
import SettingsPanel from './components/SettingsPanel';
import CollagePreview from './components/CollagePreview';
import ExportPanel from './components/ExportPanel';
import ImageGrid from './components/ImageGrid';
import type { CollageSettings, LoadedImage } from './utils/collageEngine';
import { defaultSettings, loadImages, splitIntoGroups } from './utils/collageEngine';
import './App.css';

function App() {
  const [settings, setSettings] = useState<CollageSettings>(defaultSettings);
  const [loadedImages, setLoadedImages] = useState<LoadedImage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadProgress, setLoadProgress] = useState({ loaded: 0, total: 0 });
  const [activeCollageIndex, setActiveCollageIndex] = useState(0);

  const imageGroups = useMemo(() => 
    splitIntoGroups(loadedImages, settings.imagesPerCollage),
    [loadedImages, settings.imagesPerCollage]
  );
  
  const currentGroup = useMemo(() => 
    imageGroups[activeCollageIndex] || [],
    [imageGroups, activeCollageIndex]
  );

  const handleFilesSelected = useCallback(async (files: File[]) => {
    setIsLoading(true);
    setLoadProgress({ loaded: 0, total: files.length });

    try {
      const images = await loadImages(files, (loaded, total) => {
        setLoadProgress({ loaded, total });
      });
      setLoadedImages(images);
      setActiveCollageIndex(0);
    } catch (error) {
      console.error('Failed to load images:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleAddMoreImages = useCallback(async (files: File[]) => {
    setIsLoading(true);
    setLoadProgress({ loaded: 0, total: files.length });

    try {
      const newImages = await loadImages(files, (loaded, total) => {
        setLoadProgress({ loaded, total });
      });
      setLoadedImages(prev => [...prev, ...newImages]);
    } catch (error) {
      console.error('Failed to load images:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleClearImages = useCallback(() => {
    setLoadedImages([]);
    setActiveCollageIndex(0);
  }, []);

  const handleReorderImages = useCallback((reorderedImages: LoadedImage[]) => {
    setLoadedImages(reorderedImages);
  }, []);

  const handleRotateImage = useCallback((index: number, rotation: number) => {
    setLoadedImages(prev => prev.map((img, i) => 
      i === index ? { ...img, rotation } : img
    ));
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-content">
          <div className="app-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
            </svg>
          </div>
          <div>
            <h1>Photo Collage Generator</h1>
            <p>Create stunning collages in seconds</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="sidebar">
          <div className="card">
            <div className="card-header">
              <h3>Upload Images</h3>
            </div>
            <div className="card-body">
              {loadedImages.length === 0 ? (
                <ImageUploader onFilesSelected={handleFilesSelected} disabled={isLoading} />
              ) : (
                <div className="images-loaded-section">
                  <div className="images-count">
                    <span className="count-number">{loadedImages.length}</span>
                    <span className="count-label">images loaded</span>
                  </div>
                  <ImageUploader onFilesSelected={handleAddMoreImages} disabled={isLoading} isAddMore />
                  <button className="clear-btn" onClick={handleClearImages} disabled={isLoading}>
                    Clear All Images
                  </button>
                </div>
              )}
              {isLoading && (
                <div className="loading-progress">
                  Loading: {loadProgress.loaded} / {loadProgress.total} images
                </div>
              )}
            </div>
          </div>

          {loadedImages.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3>Arrange Images</h3>
              </div>
              <div className="card-body">
                <ImageGrid
                  images={loadedImages}
                  onReorder={handleReorderImages}
                  onRotate={handleRotateImage}
                />
              </div>
            </div>
          )}

          <div className="card">
            <div className="card-header">
              <h3>Settings</h3>
            </div>
            <div className="card-body">
              <SettingsPanel
                settings={settings}
                onSettingsChange={setSettings}
                imageCount={loadedImages.length}
              />
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Export</h3>
            </div>
            <div className="card-body">
              <ExportPanel
                imageGroups={imageGroups}
                settings={settings}
                disabled={isLoading || loadedImages.length === 0}
              />
            </div>
          </div>
        </div>

        <div className="main-content">
          {imageGroups.length > 1 && (
            <div className="collage-tabs">
              {imageGroups.map((group, index) => (
                <button
                  key={index}
                  className={`collage-tab ${index === activeCollageIndex ? 'active' : ''}`}
                  onClick={() => setActiveCollageIndex(index)}
                >
                  Collage {index + 1} ({group.length})
                </button>
              ))}
            </div>
          )}

          <CollagePreview
            images={currentGroup}
            settings={settings}
            collageIndex={activeCollageIndex}
          />
        </div>
      </main>

      <footer className="app-footer">
        <p>
          All processing happens locally in your browser. Your images never leave your device.
        </p>
      </footer>
    </div>
  );
}

export default App;
