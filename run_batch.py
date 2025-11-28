#!/usr/bin/env python3
"""
Batch Collage Generator - Run without interaction.

This script runs the collage generator in batch mode without any user input.
Configure your settings directly in this file and run it to generate collages.

Usage:
  python run_batch.py
  python run_batch.py --input /path/to/images --output /path/to/output
"""

import argparse
from pathlib import Path

from collage_generator import CollageGenerator, CollageSettings, CollageShape


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Batch Collage Generator")
    parser.add_argument("--input", "-i", default="images",
                        help="Input folder containing images (default: images)")
    parser.add_argument("--output", "-o", default="Auto-Generated-Collages",
                        help="Output folder for collages (default: Auto-Generated-Collages)")
    parser.add_argument("--images-per-collage", "-n", type=int, default=50,
                        help="Number of images per collage (default: 50)")
    parser.add_argument("--size", "-s", default="3000x3000",
                        help="Canvas size WIDTHxHEIGHT (default: 3000x3000)")
    parser.add_argument("--shape", choices=["square", "rectangle", "circle", "heart"],
                        default="square", help="Collage shape (default: square)")
    parser.add_argument("--no-rounded-corners", action="store_true",
                        help="Disable rounded corners on images")
    parser.add_argument("--no-shadow", action="store_true",
                        help="Disable drop shadow on images")
    parser.add_argument("--frame", type=int, default=20,
                        help="Outer frame thickness in pixels (default: 20)")
    parser.add_argument("--spacing", type=int, default=5,
                        help="Inner spacing between images in pixels (default: 5)")
    parser.add_argument("--custom-mask", help="Path to custom PNG mask file")
    return parser.parse_args()


def main():
    """Main batch processing function."""
    args = parse_args()
    
    width, height = map(int, args.size.lower().split('x'))
    
    shape_map = {
        "square": CollageShape.SQUARE,
        "rectangle": CollageShape.RECTANGLE,
        "circle": CollageShape.CIRCLE,
        "heart": CollageShape.HEART,
    }
    shape = shape_map.get(args.shape, CollageShape.SQUARE)
    
    if args.custom_mask:
        shape = CollageShape.CUSTOM
    
    settings = CollageSettings(
        canvas_size=(width, height),
        dpi=300,
        images_per_collage=args.images_per_collage,
        outer_frame_thickness=args.frame,
        inner_spacing=args.spacing,
        enable_rounded_corners=not args.no_rounded_corners,
        enable_drop_shadow=not args.no_shadow,
        shape=shape,
        custom_mask_path=args.custom_mask
    )
    
    print("Batch Collage Generator")
    print("=" * 50)
    print(f"Input folder: {args.input}")
    print(f"Output folder: {args.output}")
    print(f"Canvas size: {width}x{height}")
    print(f"Images per collage: {args.images_per_collage}")
    print(f"Shape: {args.shape}")
    print(f"Rounded corners: {not args.no_rounded_corners}")
    print(f"Drop shadow: {not args.no_shadow}")
    print("=" * 50)
    
    if not Path(args.input).exists():
        print(f"Error: Input folder '{args.input}' not found!")
        print("Please create the folder and add your images.")
        return
    
    generator = CollageGenerator(settings)
    generator.generate_all_collages(args.input, args.output)


if __name__ == "__main__":
    main()
