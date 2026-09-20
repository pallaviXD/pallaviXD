#!/usr/bin/env python3
"""
prep_portrait.py
Preprocesses a source portrait for optimal ASCII conversion:
1. Background removal using rembg
2. Contrast Limited Adaptive Histogram Equalization (CLAHE) for sharp facial features
3. Compositing onto a solid white background
4. Crop and center to target aspect ratio
"""

import argparse
import os
import sys
import numpy as np
from PIL import Image

def preprocess_image(input_path: str, output_path: str, target_size=(400, 500)):
    print(f"Loading image from: {input_path}")
    input_img = Image.open(input_path).convert("RGBA")

    # Step 1: Background removal via rembg
    try:
        from rembg import remove
        print("Removing background using rembg...")
        nobg_img = remove(input_img)
    except Exception as e:
        print(f"Warning: rembg failed or not installed ({e}). Proceeding with original image.")
        nobg_img = input_img

    # Convert to RGBA numpy array
    np_img = np.array(nobg_img)
    
    # Composite onto solid white background
    # (subject will be illuminated, background is white/empty)
    alpha = np_img[:, :, 3] / 255.0
    rgb = np_img[:, :, :3]
    
    # White background composite
    white_bg = np.ones_like(rgb, dtype=np.float32) * 255.0
    composited = (rgb * alpha[:, :, np.newaxis] + white_bg * (1.0 - alpha[:, :, np.newaxis])).astype(np.uint8)

    # Step 2: Grayscale and CLAHE contrast enhancement
    try:
        import cv2
        gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Optional slight unsharp masking for crisp edges
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 1.5)
        sharpened = cv2.addWeighted(enhanced, 1.3, gaussian, -0.3, 0)
        final_img = Image.fromarray(sharpened)
    except Exception as e:
        print(f"Warning: cv2 CLAHE processing failed ({e}), using PIL contrast enhancement.")
        from PIL import ImageOps, ImageEnhance
        gray_img = ImageOps.grayscale(Image.fromarray(composited))
        enhancer = ImageEnhance.Contrast(gray_img)
        final_img = enhancer.enhance(1.8)

    # Step 3: Resize and crop to target proportions
    final_img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    final_img.save(output_path)
    print(f"Preprocessed image successfully saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Preprocess image for ASCII rendering")
    parser.add_argument("--input", default="assets/input_photo.png", help="Path to input photo")
    parser.add_argument("--output", default="assets/prepped_portrait.png", help="Path to output image")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.", file=sys.stderr)
        sys.exit(1)

    preprocess_image(args.input, args.output)

if __name__ == "__main__":
    main()
