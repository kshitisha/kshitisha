"""
Prep a source photo for ASCII conversion:
1. Remove background (rembg)
2. CLAHE contrast boost (OpenCV)
3. Composite on white → grayscale PNG

Usage: python scripts/prep_photo.py <source-photo.jpg>
"""
import sys
import numpy as np
import cv2
from PIL import Image

def prep(src_path):
    try:
        from rembg import remove
        with open(src_path, "rb") as f:
            raw = f.read()
        no_bg = remove(raw)
        img = Image.open(__import__("io").BytesIO(no_bg)).convert("RGBA")
        # Composite on white
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg.convert("RGB")
    except Exception as e:
        print(f"rembg failed ({e}), using original")
        img = Image.open(src_path).convert("RGB")

    img_np = np.array(img)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    enhanced = cv2.convertScaleAbs(enhanced, alpha=1.3, beta=10)
    cv2.imwrite("source-prepped.png", enhanced)
    print("Wrote source-prepped.png")

if __name__ == "__main__":
    prep(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
