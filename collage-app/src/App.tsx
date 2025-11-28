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
        <h1>Photo Collage Generator</h1>
        <p>Create beautiful photo collages right in your browser</p>
      </header>

      <main className="app-main">
        <div className="sidebar">
          <div className="upload-section">
            <h3>Upload Images</h3>
            <ImageUploader onFilesSelected={handleFilesSelected} disabled={isLoading} />
            {isLoading && (
              <div className="loading-progress">
                Loading: {loadProgress.loaded} / {loadProgress.total}
              </div>
            )}
            {loadedImages.length > 0 && !isLoading && (
              <button className="clear-btn" onClick={handleClearImages}>
                Clear All Images
              </button>
            )}
          </div>

          <SettingsPanel
            settings={settings}
            onSettingsChange={setSettings}
            imageCount={loadedImages.length}
          />

          <ExportPanel
            imageGroups={imageGroups}
            settings={settings}
            disabled={isLoading || loadedImages.length === 0}
          />
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
                  Collage {index + 1} ({group.length} images)
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
        <p>All processing happens in your browser. Your images are never uploaded to any server.</p>
      </footer>
    </div>
  );
}

export default App;
