import os
from nudenet import NudeDetector
from PIL import Image, ImageFilter

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "images", "ready_to_post") # Use your watermarked images
OUTPUT_FOLDER = os.path.join(BASE_DIR, "images", "pixiv_safe")

# Pixelation strength (Higher = bigger blocks = more censorship)
PIXEL_BLOCK_SIZE = 15 

# Parts to Censor (Pixiv Focus)
# Available: "FEMALE_BREAST", "FEMALE_GENITALIA", "ANUS", "BUTTOCKS", "MALE_GENITALIA"
TARGET_CLASSES = [
    "FEMALE_GENITALIA_EXPOSED", 
    "MALE_GENITALIA_EXPOSED", 
    "ANUS_EXPOSED", 
    "ANUS_COVERED" # Sometimes detection is tricky, safer to cover
]

def pixelate_region(image, box):
    """Applies a mosaic pixelation effect to a specific region (box)"""
    x1, y1, width, height = box
    x2, y2 = x1 + width, y1 + height
    
    # 1. Crop the sensitive area
    region = image.crop((x1, y1, x2, y2))
    
    # 2. Resize down (to lose detail)
    small_w = max(1, int(width / PIXEL_BLOCK_SIZE))
    small_h = max(1, int(height / PIXEL_BLOCK_SIZE))
    region_small = region.resize((small_w, small_h), resample=Image.BILINEAR)
    
    # 3. Resize up (to create blocks)
    region_pixelated = region_small.resize(region.size, resample=Image.NEAREST)
    
    # 4. Paste back
    image.paste(region_pixelated, (x1, y1))
    return image

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print("⏳ Loading AI Model (This might take a moment)...")
    detector = NudeDetector() # Auto-downloads model on first run

    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"🚀 Processing {len(files)} images for Pixiv censorship...")

    for filename in files:
        in_path = os.path.join(INPUT_FOLDER, filename)
        out_path = os.path.join(OUTPUT_FOLDER, filename)
        
        try:
            # Detect
            detections = detector.detect(in_path)
            
            # Open Image
            img = Image.open(in_path).convert("RGB")
            censored = False

            for detection in detections:
                label = detection['class']
                score = detection['score']
                box = detection['box'] # [x, y, w, h]

                # If it's a sensitive part and confidence is > 40%
                if label in TARGET_CLASSES and score > 0.40:
                    img = pixelate_region(img, box)
                    censored = True
                    print(f"   🍆 Censored {label} in {filename}")

            if censored:
                img.save(out_path, quality=95)
                print(f"✅ Saved Censored: {filename}")
            else:
                # If nothing detected, just copy the file (Safety)
                img.save(out_path, quality=95)
                print(f"✨ Clean image (No censorship needed): {filename}")

        except Exception as e:
            print(f"❌ Error on {filename}: {e}")

    print(f"\n🏁 Done! Check folder: {OUTPUT_FOLDER}")
    print("⚠️ REMINDER: Manually double-check images before uploading to Pixiv!")

if __name__ == "__main__":
    main()