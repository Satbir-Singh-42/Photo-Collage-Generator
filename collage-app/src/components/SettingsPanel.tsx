import type { CollageSettings, CollageShape } from '../utils/collageEngine';

interface SettingsPanelProps {
  settings: CollageSettings;
  onSettingsChange: (settings: CollageSettings) => void;
  imageCount: number;
}

export default function SettingsPanel({ settings, onSettingsChange, imageCount }: SettingsPanelProps) {
  const updateSetting = <K extends keyof CollageSettings>(key: K, value: CollageSettings[K]) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  return (
    <div className="settings-panel">
      <h3>Collage Settings</h3>
      
      <div className="setting-group">
        <label>Images Loaded</label>
        <div className="setting-value">{imageCount} images</div>
      </div>

      <div className="setting-group">
        <label htmlFor="imagesPerCollage">Images per Collage</label>
        <input
          type="number"
          id="imagesPerCollage"
          min="1"
          max="200"
          value={settings.imagesPerCollage}
          onChange={(e) => updateSetting('imagesPerCollage', parseInt(e.target.value) || 1)}
        />
      </div>

      <div className="setting-group">
        <label htmlFor="canvasWidth">Canvas Width (px)</label>
        <input
          type="number"
          id="canvasWidth"
          min="500"
          max="6000"
          step="100"
          value={settings.canvasWidth}
          onChange={(e) => updateSetting('canvasWidth', parseInt(e.target.value) || 1000)}
        />
      </div>

      <div className="setting-group">
        <label htmlFor="canvasHeight">Canvas Height (px)</label>
        <input
          type="number"
          id="canvasHeight"
          min="500"
          max="6000"
          step="100"
          value={settings.canvasHeight}
          onChange={(e) => updateSetting('canvasHeight', parseInt(e.target.value) || 1000)}
        />
      </div>

      <div className="setting-group">
        <label htmlFor="shape">Shape</label>
        <select
          id="shape"
          value={settings.shape}
          onChange={(e) => updateSetting('shape', e.target.value as CollageShape)}
        >
          <option value="square">Square</option>
          <option value="rectangle">Rectangle</option>
          <option value="circle">Circle</option>
          <option value="heart">Heart</option>
        </select>
      </div>

      <div className="setting-group">
        <label htmlFor="backgroundColor">Background Color</label>
        <input
          type="color"
          id="backgroundColor"
          value={settings.backgroundColor}
          onChange={(e) => updateSetting('backgroundColor', e.target.value)}
        />
      </div>

      <div className="setting-group">
        <label htmlFor="outerFrameThickness">Frame Thickness (px)</label>
        <input
          type="range"
          id="outerFrameThickness"
          min="0"
          max="100"
          value={settings.outerFrameThickness}
          onChange={(e) => updateSetting('outerFrameThickness', parseInt(e.target.value))}
        />
        <span className="range-value">{settings.outerFrameThickness}</span>
      </div>

      <div className="setting-group">
        <label htmlFor="innerSpacing">Inner Spacing (px)</label>
        <input
          type="range"
          id="innerSpacing"
          min="0"
          max="50"
          value={settings.innerSpacing}
          onChange={(e) => updateSetting('innerSpacing', parseInt(e.target.value))}
        />
        <span className="range-value">{settings.innerSpacing}</span>
      </div>

      <div className="setting-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={settings.enableRoundedCorners}
            onChange={(e) => updateSetting('enableRoundedCorners', e.target.checked)}
          />
          Rounded Corners
        </label>
      </div>

      {settings.enableRoundedCorners && (
        <div className="setting-group">
          <label htmlFor="roundedCornersRadius">Corner Radius (px)</label>
          <input
            type="range"
            id="roundedCornersRadius"
            min="0"
            max="50"
            value={settings.roundedCornersRadius}
            onChange={(e) => updateSetting('roundedCornersRadius', parseInt(e.target.value))}
          />
          <span className="range-value">{settings.roundedCornersRadius}</span>
        </div>
      )}

      <div className="setting-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={settings.enableDropShadow}
            onChange={(e) => updateSetting('enableDropShadow', e.target.checked)}
          />
          Drop Shadow
        </label>
      </div>

      {settings.enableDropShadow && (
        <>
          <div className="setting-group">
            <label htmlFor="shadowBlur">Shadow Blur (px)</label>
            <input
              type="range"
              id="shadowBlur"
              min="0"
              max="30"
              value={settings.shadowBlur}
              onChange={(e) => updateSetting('shadowBlur', parseInt(e.target.value))}
            />
            <span className="range-value">{settings.shadowBlur}</span>
          </div>
        </>
      )}
    </div>
  );
}
