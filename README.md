# Photo Collage Generator

Automatically generate beautiful photo collages from your image collection. Supports multiple shapes, effects, and export formats.

## Features

- Automatic folder scanning and image detection
- Auto-split large image collections into multiple collages (default: 50 images per collage)
- Multiple shape support: square, rectangle, circle, heart
- Configurable frame, borders, rounded corners, and shadows
- Dual format export (PNG and JPG)
- Error handling for corrupted images
- Both GUI and command-line interfaces
- **Non-overlapping grid layout**: Images of any size are automatically resized and placed in a clean grid with proper spacing - no overlapping guaranteed

## Requirements

- Python 3.11 or higher
- Pillow (PIL) library
- NumPy library

## Installation

1. **Clone or download this project** to your computer

2. **Install Python 3.11+** if you don't have it:
   - Download from [python.org](https://www.python.org/downloads/)

3. **Install dependencies** using pip:
   ```bash
   pip install pillow numpy
   ```

   Or if you have the pyproject.toml file, use:
   ```bash
   pip install -e .
   ```

## Usage

### Option 1: Interactive Menu (Recommended for beginners)

Run the main script for a menu-driven experience:

```bash
python main.py
```

This will show you options to:
1. Generate sample test images
2. Run the collage generator
3. Customize settings

### Option 2: Desktop GUI Application

For a visual interface similar to Shape Collage:

```bash
python gui_app.py
```

### Option 3: Batch Processing (No interaction)

For automated processing without prompts:

```bash
python run_batch.py
```

With custom paths:

```bash
python run_batch.py --input /path/to/your/images --output /path/to/output
```

### Option 4: Quick Test

Run a quick test to make sure everything works:

```bash
python quick_test.py
```

## Project Structure

```
/
├── gui_app.py               # Desktop GUI application
├── main.py                  # Interactive menu interface
├── collage_generator.py     # Core collage generation engine
├── create_sample_images.py  # Generate test images
├── run_batch.py             # Batch processing script
├── quick_test.py            # Quick test script
├── images/                  # Put your images here
└── Auto-Generated-Collages/ # Output folder (created automatically)
```

## How to Use Your Own Images

1. Create a folder called `images` in the project directory (if it doesn't exist)
2. Copy your photos into the `images` folder
3. Run one of the scripts above
4. Find your collages in the `Auto-Generated-Collages` folder

## Customization Options

When using the scripts, you can customize:

| Setting | Description | Default |
|---------|-------------|---------|
| Canvas Size | Output image dimensions | 3000x3000 pixels |
| DPI | Print resolution | 300 |
| Images per Collage | How many photos per collage | 50 |
| Shape | square, rectangle, circle, heart | square |
| Background Color | Canvas background | White |
| Frame Thickness | Outer border width | 20 pixels |
| Inner Spacing | Gap between images (prevents overlap) | 10 pixels |
| Rounded Corners | Enable/disable | Enabled |
| Drop Shadow | Enable/disable | Enabled |

## How Image Sizing Works

The generator automatically handles images of different sizes:

1. **Grid Layout**: Images are arranged in a calculated grid (e.g., 8x7 for 50 images)
2. **Smart Cropping**: Each image is cropped to fit a uniform cell size while preserving the most important part (center-focused)
3. **No Overlapping**: Every image fits within its own cell with guaranteed spacing between them
4. **Consistent Output**: Regardless of whether your photos are portrait, landscape, or square, the final collage will look clean and organized

## Supported Image Formats

- JPG / JPEG
- PNG
- GIF
- BMP
- TIFF
- WebP

## Troubleshooting

**"No module named PIL" error:**
```bash
pip install pillow
```

**"No module named numpy" error:**
```bash
pip install numpy
```

**Images not showing up:**
- Make sure your images are in the `images` folder
- Check that files have supported extensions (.jpg, .png, etc.)

**GUI not opening (Linux):**
You may need to install tkinter:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

## License

This project is open source and free to use.
