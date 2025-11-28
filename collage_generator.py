#!/usr/bin/env python3
"""
Automated Photo Collage Generator

This script automatically generates multiple photo collages from a folder of images.
Features:
- Automatic folder scanning and image detection
- Auto-split images into groups (default: 50 per collage)
- Multiple shape support: square, rectangle, circle, heart, custom mask
- Configurable frame, borders, rounded corners, and shadows
- Dual format export (PNG and JPG)
- Error handling for corrupted images
"""

import math
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from PIL import Image, ImageDraw, ImageFilter


class CollageShape(Enum):
    SQUARE = "square"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    HEART = "heart"
    CUSTOM = "custom"


@dataclass
class CollageSettings:
    """Configuration settings for collage generation."""
    canvas_size: Tuple[int, int] = (3000, 3000)
    dpi: int = 300
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    outer_frame_thickness: int = 20
    outer_frame_color: str = "#FFFFFF"
    inner_spacing: int = 5
    rounded_corners_radius: int = 10
    enable_rounded_corners: bool = True
    enable_drop_shadow: bool = True
    shadow_offset: Tuple[int, int] = (5, 5)
    shadow_blur: int = 10
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 80)
    images_per_collage: int = 50
    shape: CollageShape = CollageShape.SQUARE
    custom_mask_path: Optional[str] = None


class CollageGenerator:
    """Main class for generating photo collages."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(self, settings: Optional[CollageSettings] = None):
        self.settings = settings or CollageSettings()
        self.failed_images: List[str] = []
        
    def scan_folder(self, folder_path: str) -> List[Path]:
        """Scan folder and return list of valid image paths."""
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        images = []
        for file_path in sorted(folder.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                images.append(file_path)
        
        print(f"Found {len(images)} images in {folder_path}")
        return images
    
    def split_into_groups(self, images: List[Path]) -> List[List[Path]]:
        """Split images into equal groups based on images_per_collage setting."""
        group_size = self.settings.images_per_collage
        groups = []
        
        for i in range(0, len(images), group_size):
            group = images[i:i + group_size]
            groups.append(group)
        
        print(f"Split into {len(groups)} groups ({group_size} images per collage)")
        return groups
    
    def load_image_safely(self, image_path: Path) -> Optional[Image.Image]:
        """Load an image with error handling for corrupted files."""
        try:
            img = Image.open(image_path)
            img = img.convert('RGBA')
            img.load()
            return img
        except Exception as e:
            print(f"Warning: Skipping corrupted/unreadable image: {image_path} ({e})")
            self.failed_images.append(str(image_path))
            return None
    
    def calculate_grid(self, num_images: int) -> Tuple[int, int]:
        """Calculate optimal rows × columns for the given number of images."""
        if num_images <= 0:
            return 0, 0
        
        cols = math.ceil(math.sqrt(num_images))
        rows = math.ceil(num_images / cols)
        
        while rows * cols < num_images:
            cols += 1
        
        return rows, cols
    
    def smart_crop(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Smart crop image to fit target size while preserving aspect ratio."""
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
        
        return img.resize(target_size, Image.Resampling.LANCZOS)
    
    def add_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Add rounded corners to an image."""
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        
        output = img.copy()
        output.putalpha(mask)
        return output
    
    def add_drop_shadow(self, img: Image.Image, offset: Tuple[int, int], 
                        blur: int, color: Tuple[int, int, int, int]) -> Image.Image:
        """Add a drop shadow behind the image."""
        shadow_size = (
            img.width + abs(offset[0]) + blur * 2,
            img.height + abs(offset[1]) + blur * 2
        )
        
        shadow = Image.new('RGBA', shadow_size, (0, 0, 0, 0))
        shadow_layer = Image.new('RGBA', img.size, color)
        
        shadow.paste(shadow_layer, (blur + max(0, offset[0]), blur + max(0, offset[1])))
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        
        result = Image.new('RGBA', shadow_size, (0, 0, 0, 0))
        result.paste(shadow, (0, 0))
        
        paste_x = blur + max(0, -offset[0])
        paste_y = blur + max(0, -offset[1])
        result.paste(img, (paste_x, paste_y), img if img.mode == 'RGBA' else None)
        
        return result
    
    def create_shape_mask(self, size: Tuple[int, int], shape: CollageShape, 
                          custom_mask_path: Optional[str] = None) -> Image.Image:
        """Create a mask for the specified shape."""
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        
        if shape == CollageShape.SQUARE or shape == CollageShape.RECTANGLE:
            draw.rectangle([(0, 0), size], fill=255)
            
        elif shape == CollageShape.CIRCLE:
            min_dim = min(size)
            center = (size[0] // 2, size[1] // 2)
            radius = min_dim // 2
            draw.ellipse([
                center[0] - radius, center[1] - radius,
                center[0] + radius, center[1] + radius
            ], fill=255)
            
        elif shape == CollageShape.HEART:
            self._draw_heart_shape(draw, size)
            
        elif shape == CollageShape.CUSTOM and custom_mask_path:
            try:
                custom_mask = Image.open(custom_mask_path).convert('L')
                custom_mask = custom_mask.resize(size, Image.Resampling.LANCZOS)
                return custom_mask
            except Exception as e:
                print(f"Warning: Could not load custom mask, using square: {e}")
                draw.rectangle([(0, 0), size], fill=255)
        
        return mask
    
    def _draw_heart_shape(self, draw: ImageDraw.ImageDraw, size: Tuple[int, int]):
        """Draw a heart shape on the given ImageDraw object."""
        width, height = size
        center_x = width // 2
        scale = min(width, height) / 2
        
        points = []
        for i in range(360):
            t = math.radians(i)
            x = 16 * (math.sin(t) ** 3)
            y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            
            px = center_x + int(x * scale / 18)
            py = int(height * 0.45) + int(y * scale / 18)
            points.append((px, py))
        
        draw.polygon(points, fill=255)
    
    def create_collage(self, images: List[Path], collage_index: int) -> Optional[Image.Image]:
        """Create a single collage from a list of images."""
        loaded_images = []
        for img_path in images:
            img = self.load_image_safely(img_path)
            if img:
                loaded_images.append(img)
        
        if not loaded_images:
            print(f"Warning: No valid images for collage {collage_index}")
            return None
        
        rows, cols = self.calculate_grid(len(loaded_images))
        print(f"Collage {collage_index}: {len(loaded_images)} images in {rows}x{cols} grid")
        
        canvas_w, canvas_h = self.settings.canvas_size
        frame = self.settings.outer_frame_thickness
        spacing = self.settings.inner_spacing
        
        usable_w = canvas_w - (2 * frame) - ((cols - 1) * spacing)
        usable_h = canvas_h - (2 * frame) - ((rows - 1) * spacing)
        
        cell_w = usable_w // cols
        cell_h = usable_h // rows
        
        shadow_padding = 0
        if self.settings.enable_drop_shadow:
            shadow_padding = self.settings.shadow_blur + max(
                abs(self.settings.shadow_offset[0]),
                abs(self.settings.shadow_offset[1])
            )
        
        img_w = cell_w - (2 * shadow_padding)
        img_h = cell_h - (2 * shadow_padding)
        
        if img_w <= 0 or img_h <= 0:
            img_w = max(10, cell_w - 10)
            img_h = max(10, cell_h - 10)
            shadow_padding = 5
        
        canvas = Image.new('RGBA', self.settings.canvas_size, self.settings.background_color)
        
        for idx, img in enumerate(loaded_images):
            row = idx // cols
            col = idx % cols
            
            processed_img = self.smart_crop(img, (img_w, img_h))
            
            if self.settings.enable_rounded_corners:
                processed_img = self.add_rounded_corners(
                    processed_img, 
                    self.settings.rounded_corners_radius
                )
            
            if self.settings.enable_drop_shadow:
                processed_img = self.add_drop_shadow(
                    processed_img,
                    self.settings.shadow_offset,
                    self.settings.shadow_blur,
                    self.settings.shadow_color
                )
            
            x = frame + col * (cell_w + spacing) + (cell_w - processed_img.width) // 2
            y = frame + row * (cell_h + spacing) + (cell_h - processed_img.height) // 2
            
            canvas.paste(processed_img, (x, y), processed_img)
        
        if self.settings.shape != CollageShape.SQUARE and self.settings.shape != CollageShape.RECTANGLE:
            mask = self.create_shape_mask(
                self.settings.canvas_size, 
                self.settings.shape,
                self.settings.custom_mask_path
            )
            
            bg = Image.new('RGBA', self.settings.canvas_size, (0, 0, 0, 0))
            bg.paste(canvas, (0, 0))
            bg.putalpha(mask)
            canvas = bg
        
        return canvas
    
    def save_collage(self, collage: Image.Image, output_folder: Path, index: int):
        """Save collage in both PNG and JPG formats."""
        base_name = f"collage_{index:02d}"
        
        png_path = output_folder / f"{base_name}.png"
        collage.save(png_path, 'PNG', dpi=(self.settings.dpi, self.settings.dpi))
        print(f"Saved: {png_path}")
        
        jpg_path = output_folder / f"{base_name}.jpg"
        rgb_collage = Image.new('RGB', collage.size, (255, 255, 255))
        rgb_collage.paste(collage, (0, 0), collage if collage.mode == 'RGBA' else None)
        rgb_collage.save(jpg_path, 'JPEG', quality=95, dpi=(self.settings.dpi, self.settings.dpi))
        print(f"Saved: {jpg_path}")
    
    def generate_all_collages(self, input_folder: str, output_folder: str = "Auto-Generated-Collages"):
        """Main method to generate all collages from an input folder."""
        print("=" * 60)
        print("AUTOMATED PHOTO COLLAGE GENERATOR")
        print("=" * 60)
        
        images = self.scan_folder(input_folder)
        if not images:
            print("No images found in the specified folder.")
            return
        
        groups = self.split_into_groups(images)
        
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)
        print(f"\nOutput folder: {output_path.absolute()}")
        
        print("\n" + "-" * 60)
        print("GENERATING COLLAGES")
        print("-" * 60)
        
        successful = 0
        for i, group in enumerate(groups, 1):
            print(f"\nProcessing collage {i}/{len(groups)}...")
            collage = self.create_collage(group, i)
            
            if collage:
                self.save_collage(collage, output_path, i)
                successful += 1
        
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        print(f"Total collages generated: {successful}/{len(groups)}")
        print(f"Output folder: {output_path.absolute()}")
        
        if self.failed_images:
            print(f"\nSkipped {len(self.failed_images)} corrupted/unreadable images:")
            for img in self.failed_images[:10]:
                print(f"  - {img}")
            if len(self.failed_images) > 10:
                print(f"  ... and {len(self.failed_images) - 10} more")


def main():
    """Main entry point for the collage generator."""
    settings = CollageSettings(
        canvas_size=(3000, 3000),
        dpi=300,
        background_color=(255, 255, 255, 255),
        outer_frame_thickness=20,
        outer_frame_color="#FFFFFF",
        inner_spacing=5,
        rounded_corners_radius=10,
        enable_rounded_corners=True,
        enable_drop_shadow=True,
        shadow_offset=(5, 5),
        shadow_blur=10,
        shadow_color=(0, 0, 0, 80),
        images_per_collage=50,
        shape=CollageShape.SQUARE,
        custom_mask_path=None
    )
    
    generator = CollageGenerator(settings)
    
    input_folder = "images"
    
    if not Path(input_folder).exists():
        print(f"Creating sample input folder: {input_folder}/")
        print("Please add your images to this folder and run the script again.")
        Path(input_folder).mkdir(exist_ok=True)
        return
    
    generator.generate_all_collages(input_folder)


if __name__ == "__main__":
    main()
