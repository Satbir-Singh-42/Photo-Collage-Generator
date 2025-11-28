import { useState, useCallback, useMemo } from 'react';
import ImageUploader from './components/ImageUploader';
import SettingsPanel from './components/SettingsPanel';
import CollagePreview from './components/CollagePreview';
import ExportPanel from './components/ExportPanel';
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

  const handleClearImages = useCallback(() => {
    setLoadedImages([]);
    setActiveCollageIndex(0);
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
              <ImageUploader onFilesSelected={handleFilesSelected} disabled={isLoading} />
              {isLoading && (
                <div className="loading-progress">
                  Loading: {loadProgress.loaded} / {loadProgress.total} images
                </div>
              )}
              {loadedImages.length > 0 && !isLoading && (
                <button className="clear-btn" onClick={handleClearImages}>
                  Clear All Images
                </button>
              )}
            </div>
          </div>

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
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          All processing happens locally in your browser. Your images never leave your device.
        </p>
      </footer>
    </div>
  );
}

export default App;
