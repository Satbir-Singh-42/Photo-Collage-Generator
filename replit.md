# Automated Photo Collage Generator

## Overview

This project automatically generates multiple photo collages from a folder containing images. It handles everything from scanning folders, grouping images, creating beautifully laid-out collages with various shapes and effects, to exporting in multiple formats.

## Project Structure

```
/
├── main.py                  # Interactive menu-driven interface
├── collage_generator.py     # Core collage generation engine
├── create_sample_images.py  # Sample image generator for testing
├── run_batch.py             # Non-interactive batch processing
├── quick_test.py            # Quick test script
├── images/                  # Input folder for your images
└── Auto-Generated-Collages/ # Output folder for generated collages
```

## How to Use

### Interactive Mode
Run `python main.py` to use the interactive menu:
1. Generate sample images for testing
2. Generate collages with default settings
3. Generate collages with custom settings
4. View current settings
5. Exit

### Batch Mode
Run `python run_batch.py` with optional arguments:
```bash
python run_batch.py --input images --output output --images-per-collage 50 --shape circle
```

Options:
- `--input`, `-i`: Input folder (default: images)
- `--output`, `-o`: Output folder (default: Auto-Generated-Collages)
- `--images-per-collage`, `-n`: Images per collage (default: 50)
- `--size`, `-s`: Canvas size (default: 3000x3000)
- `--shape`: square, rectangle, circle, heart (default: square)
- `--frame`: Outer frame thickness (default: 20)
- `--spacing`: Inner spacing (default: 5)
- `--no-rounded-corners`: Disable rounded corners
- `--no-shadow`: Disable drop shadows
- `--custom-mask`: Path to custom PNG mask

## Features

### Image Processing
- Automatic folder scanning (JPG, JPEG, PNG, GIF, BMP, TIFF, WebP)
- Auto-split into groups (configurable images per collage)
- Error handling for corrupted/unreadable images

### Collage Settings
- Canvas size: 3000×3000 px (configurable)
- Resolution: 300 DPI (print quality)
- Background: White (RGBA)

### Shape Options
- Square
- Rectangle
- Circle
- Heart
- Custom PNG mask

### Frame & Border
- Outer frame: 20px white border
- Inner spacing: 5px between images
- Rounded corners: 10px radius (optional)
- Drop shadow: Soft shadow behind each photo (optional)

### Layout
- Automatic grid calculation (rows × columns)
- Aspect ratio preservation
- Smart cropping for shape fitting
- Even and symmetrical arrangement

### Export
- Dual format: PNG and JPG
- Sequential naming: collage_01, collage_02, etc.
- Organized output folder

## Dependencies

- Python 3.11
- Pillow (PIL) for image processing
- NumPy for calculations

## Recent Changes

- Initial project setup with full collage generator
- Added interactive menu (main.py)
- Added batch processing (run_batch.py)
- Implemented all shape types (square, rectangle, circle, heart, custom mask)
- Added rounded corners and drop shadow effects
- Dual format export (PNG/JPG)
- Error handling for corrupted images
