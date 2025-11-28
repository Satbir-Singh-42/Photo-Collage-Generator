#!/usr/bin/env python3
"""
Create sample images for testing the collage generator.
Generates colorful images with random patterns and gradients.
"""

import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def create_gradient_image(width: int, height: int, color1: tuple, color2: tuple) -> Image.Image:
    """Create a gradient image from color1 to color2."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    if pixels is None:
        return img
    
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    return img


def add_pattern(img: Image.Image, pattern_type: str) -> Image.Image:
    """Add a decorative pattern to the image."""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    if pattern_type == "circles":
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(20, 100)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255), 150)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=None, outline='white', width=3)
    
    elif pattern_type == "lines":
        for i in range(0, width, 30):
            draw.line([(i, 0), (i + height//2, height)], fill='white', width=2)
    
    elif pattern_type == "dots":
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(3, 8)
            draw.ellipse([x-r, y-r, x+r, y+r], fill='white')
    
    elif pattern_type == "squares":
        for _ in range(8):
            x = random.randint(0, width - 40)
            y = random.randint(0, height - 40)
            size = random.randint(20, 60)
            draw.rectangle([x, y, x+size, y+size], outline='white', width=2)
    
    return img


def add_number_label(img: Image.Image, number: int) -> Image.Image:
    """Add a number label to the center of the image."""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    text = str(number)
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.rectangle([x-10, y-5, x+text_width+10, y+text_height+5], fill=(0, 0, 0, 128))
    draw.text((x, y), text, fill='white')
    
    return img


def generate_sample_images(output_folder: str = "images", count: int = 100):
    """Generate sample images for testing the collage generator."""
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    color_palettes = [
        ((255, 107, 107), (255, 230, 109)),
        ((78, 205, 196), (199, 244, 100)),
        ((107, 185, 240), (147, 112, 219)),
        ((255, 154, 162), (255, 218, 193)),
        ((118, 200, 147), (252, 238, 33)),
        ((255, 195, 113), (255, 95, 109)),
        ((162, 155, 254), (253, 255, 182)),
        ((97, 97, 97), (155, 197, 61)),
        ((255, 87, 87), (255, 189, 68)),
        ((58, 134, 255), (131, 56, 236)),
    ]
    
    patterns = ["circles", "lines", "dots", "squares", "none"]
    sizes = [(400, 400), (600, 400), (400, 600), (500, 500), (800, 600)]
    
    print(f"Generating {count} sample images in '{output_folder}'...")
    
    for i in range(1, count + 1):
        palette = random.choice(color_palettes)
        size = random.choice(sizes)
        pattern = random.choice(patterns)
        
        img = create_gradient_image(size[0], size[1], palette[0], palette[1])
        
        if pattern != "none":
            img = add_pattern(img, pattern)
        
        img = add_number_label(img, i)
        
        filename = output_path / f"sample_{i:04d}.jpg"
        img.save(filename, 'JPEG', quality=90)
        
        if i % 20 == 0:
            print(f"  Generated {i}/{count} images...")
    
    print(f"Done! Created {count} sample images in '{output_folder}'")


if __name__ == "__main__":
    generate_sample_images("images", 100)
