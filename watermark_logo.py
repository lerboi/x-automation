import os
from PIL import Image
from tqdm import tqdm

# --- CONFIGURATION ---
# Base directory is where this script runs (root/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Input: Raw images to be watermarked
INPUT_FOLDER = os.path.join(BASE_DIR, "watermark_data", "input")

# 2. Output: Where the finished watermarked files go
OUTPUT_FOLDER = os.path.join(BASE_DIR, "watermark_data", "output")

# 3. Logo: Located in watermark_data folder
WATERMARK_FILE = os.path.join(BASE_DIR, "watermark_data", "watermark.png")

# --- WATERMARK SETTINGS ---
LOGO_SCALE = 0.45   # Logo size relative to image width (0.45 = 45% - increased from 35%)
OPACITY = 215       # Transparency (0=invisible, 255=solid) - fully opaque (already at max)
PADDING_X = 15      # Pixel distance from right edge
PADDING_Y = -10       # Pixel distance from bottom edge (smaller = lower position)

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
        x_pos = base_w - new_logo_w - PADDING_X
        y_pos = base_h - new_logo_h - PADDING_Y

        # 5. Paste & Composite
        transparent_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        transparent_layer.paste(resized_logo, (x_pos, y_pos), mask=resized_logo)
        final = Image.alpha_composite(base_image, transparent_layer)

        # 6. Save as JPG with corrected extension
        # Force .jpg extension regardless of input format
        output_path = os.path.splitext(output_path)[0] + ".jpg"
        final.convert("RGB").save(output_path, "JPEG", quality=95)

    except Exception as e:
        # Use tqdm.write to avoid breaking progress bar
        tqdm.write(f"❌ Error processing {os.path.basename(image_path)}: {e}")

def detect_mode(input_folder):
    """
    Auto-detect processing mode based on input folder contents.
    Returns: 'recursive' if subdirectories found, 'flat' if only images found
    """
    try:
        items = os.listdir(input_folder)
        for item in items:
            item_path = os.path.join(input_folder, item)
            if os.path.isdir(item_path):
                return 'recursive'
        return 'flat'
    except Exception:
        return 'flat'

def process_flat_mode(watermark_source):
    """
    Flat mode: Process images directly in input folder.
    Backwards compatible with original behavior.
    """
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not files:
        print(f"⚠️ No images found in: {INPUT_FOLDER}")
        return 0

    print(f"🚀 Processing {len(files)} images (Flat Mode)...")
    
    count = 0
    for filename in tqdm(files, desc="Watermarking", unit="img", ncols=80):
        in_path = os.path.join(INPUT_FOLDER, filename)
        # Add _wm suffix before extension
        name_without_ext = os.path.splitext(filename)[0]
        out_filename = f"{name_without_ext}_wm.jpg"
        out_path = os.path.join(OUTPUT_FOLDER, out_filename)
        add_logo_watermark(in_path, out_path, watermark_source)
        count += 1

    return count

def process_recursive_mode(watermark_source):
    """
    Recursive mode: Preserve folder structure with _wm suffix on folders.
    Walks through all subdirectories and processes images while maintaining structure.
    """
    # First, count total images for progress bar
    total_images = 0
    for root, dirs, files in os.walk(INPUT_FOLDER):
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        total_images += len(image_files)
    
    if total_images == 0:
        print(f"⚠️ No images found in subdirectories")
        return 0
    
    print(f"🚀 Processing {total_images} images across folders (Recursive Mode)...")
    
    count = 0
    # Create progress bar
    with tqdm(total=total_images, desc="Watermarking", unit="img", ncols=80) as pbar:
        # Walk through all subdirectories in input folder
        for root, dirs, files in os.walk(INPUT_FOLDER):
            # Calculate relative path from input folder
            rel_path = os.path.relpath(root, INPUT_FOLDER)
            
            # Skip if we're at the root level (no subdirectories to process)
            if rel_path == '.':
                continue
            
            # Split the relative path to add _wm suffix to the top-level folder
            path_parts = rel_path.split(os.sep)
            if len(path_parts) > 0:
                # Add _wm suffix to the top-level folder only
                path_parts[0] = path_parts[0] + '_wm'
            
            # Reconstruct the output path
            output_rel_path = os.sep.join(path_parts)
            output_dir = os.path.join(OUTPUT_FOLDER, output_rel_path)
            
            # Create output directory structure
            os.makedirs(output_dir, exist_ok=True)
            
            # Process all image files in this directory
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            
            for filename in image_files:
                in_path = os.path.join(root, filename)
                # Add _wm suffix to filename before extension
                name_without_ext = os.path.splitext(filename)[0]
                out_filename = f"{name_without_ext}_wm.jpg"
                out_path = os.path.join(output_dir, out_filename)
                add_logo_watermark(in_path, out_path, watermark_source)
                count += 1
                pbar.update(1)
    
    return count

def main():
    print("--- 🌊 Watermark Tool Starting ---")
    
    # Auto-create folders if they don't exist
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"⚠️ Created input folder: {INPUT_FOLDER}")
        print("👉 Please put your images in there and run this again.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    if not os.path.exists(WATERMARK_FILE):
        print(f"❌ Error: 'watermark.png' not found in watermark_data folder!")
        return

    # Load watermark
    try:
        watermark_source = Image.open(WATERMARK_FILE).convert("RGBA")
    except Exception as e:
        print(f"❌ Error loading watermark image: {e}")
        return

    # Auto-detect mode
    mode = detect_mode(INPUT_FOLDER)
    print(f"📂 Mode detected: {mode.upper()}")
    
    # Process based on detected mode
    if mode == 'flat':
        count = process_flat_mode(watermark_source)
    else:  # recursive
        count = process_recursive_mode(watermark_source)
    
    if count > 0:
        print(f"\n✨ SUCCESS! {count} images watermarked and saved to: watermark_data/output/")
    else:
        print(f"\n⚠️ No images were processed.")

if __name__ == "__main__":
    main()