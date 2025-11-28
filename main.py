#!/usr/bin/env python3
"""
Main entry point for the Automated Photo Collage Generator.

This script provides a menu-driven interface to:
1. Generate sample images for testing
2. Run the collage generator with various settings
3. Customize collage parameters
"""

import sys
from pathlib import Path

from collage_generator import CollageGenerator, CollageSettings, CollageShape
from create_sample_images import generate_sample_images


def print_header():
    """Print the application header."""
    print("\n" + "=" * 70)
    print("       AUTOMATED PHOTO COLLAGE GENERATOR")
    print("=" * 70)
    print()


def print_menu():
    """Print the main menu."""
    print("\nOptions:")
    print("  1. Generate sample images for testing")
    print("  2. Generate collages (default settings)")
    print("  3. Generate collages (custom settings)")
    print("  4. Show current settings")
    print("  5. Exit")
    print()


def get_shape_choice() -> CollageShape:
    """Get shape choice from user."""
    print("\nAvailable shapes:")
    print("  1. Square")
    print("  2. Rectangle")
    print("  3. Circle")
    print("  4. Heart")
    print("  5. Custom mask")
    
    while True:
        try:
            choice = input("Select shape (1-5) [default: 1]: ").strip() or "1"
            choice_num = int(choice)
            shapes = {
                1: CollageShape.SQUARE,
                2: CollageShape.RECTANGLE,
                3: CollageShape.CIRCLE,
                4: CollageShape.HEART,
                5: CollageShape.CUSTOM
            }
            if choice_num in shapes:
                return shapes[choice_num]
            print("Invalid choice. Please enter 1-5.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_custom_settings() -> CollageSettings:
    """Get custom settings from user."""
    print("\n--- Custom Collage Settings ---")
    
    try:
        size_input = input("Canvas size (e.g., 3000x3000) [default: 3000x3000]: ").strip() or "3000x3000"
        width, height = map(int, size_input.lower().split('x'))
        
        images_per = input("Images per collage [default: 50]: ").strip() or "50"
        images_per_num = int(images_per)
        
        spacing = input("Inner spacing between images in pixels [default: 5]: ").strip() or "5"
        spacing_num = int(spacing)
        
        frame = input("Outer frame thickness in pixels [default: 20]: ").strip() or "20"
        frame_num = int(frame)
        
        corners = input("Enable rounded corners? (y/n) [default: y]: ").strip().lower() or "y"
        enable_corners = corners == 'y'
        
        shadow = input("Enable drop shadow? (y/n) [default: y]: ").strip().lower() or "y"
        enable_shadow = shadow == 'y'
        
        shape = get_shape_choice()
        
        custom_mask = None
        if shape == CollageShape.CUSTOM:
            custom_mask = input("Path to custom mask PNG: ").strip()
        
        return CollageSettings(
            canvas_size=(width, height),
            dpi=300,
            images_per_collage=images_per_num,
            inner_spacing=spacing_num,
            outer_frame_thickness=frame_num,
            enable_rounded_corners=enable_corners,
            enable_drop_shadow=enable_shadow,
            shape=shape,
            custom_mask_path=custom_mask if custom_mask else None
        )
        
    except (ValueError, Exception) as e:
        print(f"Error in settings: {e}. Using defaults.")
        return CollageSettings()


def show_settings(settings: CollageSettings):
    """Display current settings."""
    print("\n--- Current Settings ---")
    print(f"  Canvas Size: {settings.canvas_size[0]}x{settings.canvas_size[1]} px")
    print(f"  Resolution: {settings.dpi} DPI")
    print(f"  Background: White (RGBA)")
    print(f"  Images per Collage: {settings.images_per_collage}")
    print(f"  Outer Frame: {settings.outer_frame_thickness}px ({settings.outer_frame_color})")
    print(f"  Inner Spacing: {settings.inner_spacing}px")
    print(f"  Rounded Corners: {'Yes' if settings.enable_rounded_corners else 'No'} (radius: {settings.rounded_corners_radius}px)")
    print(f"  Drop Shadow: {'Yes' if settings.enable_drop_shadow else 'No'}")
    print(f"  Shape: {settings.shape.value}")
    if settings.custom_mask_path:
        print(f"  Custom Mask: {settings.custom_mask_path}")
    print()


def run_generator(settings: CollageSettings, input_folder: str = "images"):
    """Run the collage generator with given settings."""
    if not Path(input_folder).exists():
        print(f"\nError: Input folder '{input_folder}' not found!")
        print("Please create the folder and add images, or generate sample images first.")
        return
    
    images = list(Path(input_folder).iterdir())
    image_count = sum(1 for f in images if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'})
    
    if image_count == 0:
        print(f"\nNo images found in '{input_folder}'!")
        print("Please add images or generate sample images first.")
        return
    
    print(f"\nFound {image_count} images in '{input_folder}'")
    confirm = input("Proceed with collage generation? (y/n) [default: y]: ").strip().lower() or "y"
    
    if confirm != 'y':
        print("Generation cancelled.")
        return
    
    generator = CollageGenerator(settings)
    generator.generate_all_collages(input_folder)


def main():
    """Main entry point."""
    print_header()
    
    settings = CollageSettings()
    input_folder = "images"
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            try:
                count = input("How many sample images to generate? [default: 100]: ").strip() or "100"
                count_num = int(count)
                generate_sample_images(input_folder, count_num)
            except ValueError:
                print("Invalid number. Using default (100).")
                generate_sample_images(input_folder, 100)
        
        elif choice == "2":
            print("\nUsing default settings:")
            show_settings(settings)
            run_generator(settings, input_folder)
        
        elif choice == "3":
            settings = get_custom_settings()
            show_settings(settings)
            run_generator(settings, input_folder)
        
        elif choice == "4":
            show_settings(settings)
        
        elif choice == "5":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
