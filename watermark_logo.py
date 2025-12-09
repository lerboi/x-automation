import os
from PIL import Image

# --- CONFIGURATION ---
# Base directory is where this script runs (root/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Input: The new specific folder for raw images
INPUT_FOLDER = os.path.join(BASE_DIR, "images", "input_for_watermark")

# 2. Output: Where the finished files go
OUTPUT_FOLDER = os.path.join(BASE_DIR, "images", "ready_to_post")

# 3. Logo: Located in the root folder
WATERMARK_FILE = os.path.join(BASE_DIR, "watermark.png")

# --- WATERMARK SETTINGS ---
LOGO_SCALE = 0.25   # Logo size relative to image width (0.25 = 25%)
OPACITY = 200       # Transparency (0=invisible, 255=solid)
PADDING = 40        # Pixel distance from bottom-right corner

def add_logo_watermark(image_path, output_path, watermark_img):
    try:
        base_image = Image.open(image_path).convert("RGBA")
        base_w, base_h = base_image.size

        # 1. Calculate new Logo Size (Proportional)
        logo_aspect = watermark_img.width / watermark_img.height
        new_logo_w = int(base_w * LOGO_SCALE)
        new_logo_h = int(new_logo_w / logo_aspect)

        # 2. Resize the Watermark
        resized_logo = watermark_img.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)

        # 3. Adjust Opacity
        if OPACITY < 255:
            r, g, b, alpha = resized_logo.split()
            alpha = alpha.point(lambda p: p * (OPACITY / 255))
            resized_logo = Image.merge("RGBA", (r, g, b, alpha))

        # 4. Calculate Position (Bottom Right)
        x_pos = base_w - new_logo_w - PADDING
        y_pos = base_h - new_logo_h - PADDING

        # 5. Paste & Composite
        transparent_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        transparent_layer.paste(resized_logo, (x_pos, y_pos), mask=resized_logo)
        final = Image.alpha_composite(base_image, transparent_layer)

        # 6. Save as JPG
        final.convert("RGB").save(output_path, "JPEG", quality=95)
        print(f"✅ Stamped: {os.path.basename(image_path)}")

    except Exception as e:
        print(f"❌ Error processing {os.path.basename(image_path)}: {e}")

def main():
    print("--- 🌊 Root Watermarker Starting ---")
    
    # Auto-create folders if they don't exist
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"⚠️ Created input folder: {INPUT_FOLDER}")
        print("👉 Please put your images in there and run this again.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    if not os.path.exists(WATERMARK_FILE):
        print(f"❌ Error: 'watermark.png' not found in root folder!")
        return

    # Load watermark
    try:
        watermark_source = Image.open(WATERMARK_FILE).convert("RGBA")
    except Exception as e:
        print(f"❌ Error loading watermark image: {e}")
        return

    # Process Images
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not files:
        print(f"⚠️ No images found in: {INPUT_FOLDER}")
        return

    print(f"🚀 Processing {len(files)} images...")
    
    count = 0
    for filename in files:
        in_path = os.path.join(INPUT_FOLDER, filename)
        out_path = os.path.join(OUTPUT_FOLDER, filename)
        add_logo_watermark(in_path, out_path, watermark_source)
        count += 1

    print(f"\n✨ SUCCESS! {count} images saved to: images/ready_to_post/")

if __name__ == "__main__":
    main()