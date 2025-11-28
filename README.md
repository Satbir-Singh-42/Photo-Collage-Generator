# Photo Collage Generator

A React web application that creates beautiful photo collages right in your browser. All processing happens client-side - your images are never uploaded to any server.

## Features

- Drag & drop image upload
- Support for JPG, PNG, GIF, BMP, WebP, and TIFF formats
- Multiple shape support: square, rectangle, circle, heart
- Configurable settings:
  - Canvas size (width/height)
  - Images per collage
  - Background color
  - Frame thickness and inner spacing
  - Rounded corners
  - Drop shadows
- Non-overlapping grid layout - images are automatically sized to fit
- Export as PNG (high quality) or JPG (smaller file size)
- Split large image collections into multiple collages automatically
- Live preview as you adjust settings

## Local Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

## Deploy to Vercel

### Option 1: Deploy from GitHub

1. Push this `collage-app` folder to a GitHub repository
2. Go to [vercel.com](https://vercel.com) and sign in
3. Click "New Project" and import your repository
4. Vercel will auto-detect the Vite framework
5. Click "Deploy"

### Option 2: Deploy with Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Deploy (from the collage-app folder)
vercel
```

### Option 3: Manual Upload

1. Run `npm run build` to create the production build
2. Go to [vercel.com](https://vercel.com) and sign in
3. Drag and drop the `dist` folder to deploy

## Project Structure

```
collage-app/
├── src/
│   ├── components/
│   │   ├── ImageUploader.tsx    # Drag & drop upload zone
│   │   ├── SettingsPanel.tsx    # Collage configuration controls
│   │   ├── CollagePreview.tsx   # Live preview of the collage
│   │   └── ExportPanel.tsx      # Export format selection & download
│   ├── utils/
│   │   └── collageEngine.ts     # Core collage generation logic
│   ├── App.tsx                  # Main application component
│   ├── App.css                  # Application styles
│   ├── main.tsx                 # React entry point
│   └── index.css                # Global styles
├── public/                      # Static assets
├── vercel.json                  # Vercel deployment config
├── vite.config.ts               # Vite configuration
├── package.json                 # Dependencies and scripts
└── tsconfig.json                # TypeScript configuration
```

## How It Works

1. **Upload Images**: Drag and drop or click to select multiple images
2. **Configure Settings**: Adjust canvas size, shape, spacing, and effects
3. **Preview**: See your collage update in real-time
4. **Export**: Download as PNG or JPG

The collage generator uses the HTML5 Canvas API to:
- Smart-crop images to fit uniformly in a grid
- Apply rounded corners and drop shadows
- Apply shape masks (circle, heart)
- Generate high-resolution output files

## Browser Support

Works in all modern browsers:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

Open source - free to use and modify.
