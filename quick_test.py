#!/usr/bin/env python3
"""
Quick test script to verify collage generation works correctly.
This runs a non-interactive test with sample images.
"""

from pathlib import Path
from collage_generator import CollageGenerator, CollageSettings, CollageShape
from create_sample_images import generate_sample_images


def run_quick_test():
    """Run a quick test of the collage generator."""
    print("=" * 60)
    print("QUICK TEST - AUTOMATED COLLAGE GENERATOR")
    print("=" * 60)
    
    input_folder = "images"
    if not Path(input_folder).exists():
        Path(input_folder).mkdir(exist_ok=True)
    
    existing_images = list(Path(input_folder).glob("*.jpg")) + list(Path(input_folder).glob("*.png"))
    if len(existing_images) < 10:
        print(f"\nGenerating 60 sample images for testing...")
        generate_sample_images(input_folder, 60)
    else:
        print(f"\nFound {len(existing_images)} existing images in '{input_folder}'")
    
    settings = CollageSettings(
        canvas_size=(3000, 3000),
        dpi=300,
        images_per_collage=20,
        outer_frame_thickness=20,
        inner_spacing=5,
        enable_rounded_corners=True,
        enable_drop_shadow=True,
        shape=CollageShape.SQUARE
    )
    
    print("\nTest Settings:")
    print(f"  Canvas: {settings.canvas_size[0]}x{settings.canvas_size[1]} px")
    print(f"  Images per collage: {settings.images_per_collage}")
    print(f"  Shape: {settings.shape.value}")
    
    generator = CollageGenerator(settings)
    generator.generate_all_collages(input_folder)
    
    output_folder = Path("Auto-Generated-Collages")
    if output_folder.exists():
        png_files = list(output_folder.glob("*.png"))
        jpg_files = list(output_folder.glob("*.jpg"))
        print(f"\n--- TEST RESULTS ---")
        print(f"PNG files created: {len(png_files)}")
        print(f"JPG files created: {len(jpg_files)}")
        
        for f in sorted(output_folder.iterdir())[:10]:
            print(f"  - {f.name}")
    
    print("\nQuick test completed!")


if __name__ == "__main__":
    run_quick_test()
