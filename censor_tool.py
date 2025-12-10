import os
from nudenet import NudeDetector
from PIL import Image
from tqdm import tqdm

# --- AGGRESSIVE NUDENET CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "censor_data", "input")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "censor_data", "output")

# Pixelation strength (Higher = bigger blocks = more censorship)
PIXEL_BLOCK_SIZE = 25

# AGGRESSIVE: Very low confidence threshold to catch everything possible
CONFIDENCE_THRESHOLD = 0.08  # 8% confidence (was 0.25)

# AGGRESSIVE: Large padding to ensure full coverage
BOX_PADDING = 70  # 70px padding (was 45)

# Classes to censor - ONLY GENITALIA AND ANUS
TARGET_CLASSES = [
    "FEMALE_GENITALIA_EXPOSED",
    "FEMALE_GENITALIA_COVERED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED",
    "ANUS_COVERED",
]

def pixelate_region(image, box, padding=BOX_PADDING):
    """Applies a mosaic pixelation effect to a specific region (box) with padding"""
    x1, y1, width, height = box
    
    # Add padding to ensure full coverage
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    width = width + (padding * 2)
    height = height + (padding * 2)
    
    # Ensure we don't exceed image boundaries
    x2 = min(image.width, x1 + width)
    y2 = min(image.height, y1 + height)
    
    # Recalculate width and height after boundary checks
    width = x2 - x1
    height = y2 - y1
    
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

def process_single_image(detector, in_path, out_path):
    """Process a single image for censorship. Returns (True, num_censored) if processed successfully."""
    try:
        # Detect
        detections = detector.detect(in_path)
        
        # Open Image
        img = Image.open(in_path).convert("RGB")
        censored_count = 0

        for detection in detections:
            label = detection['class']
            score = detection['score']
            box = detection['box']  # [x, y, w, h]

            # If it's a sensitive part and confidence meets threshold
            if label in TARGET_CLASSES and score > CONFIDENCE_THRESHOLD:
                img = pixelate_region(img, box)
                censored_count += 1

        # Save the image (whether censored or clean)
        img.save(out_path, quality=95)
        return True, censored_count

    except Exception as e:
        tqdm.write(f"❌ Error on {os.path.basename(in_path)}: {e}")
        return False, 0

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

def process_flat_mode(detector):
    """
    Flat mode: Process images directly in input folder.
    """
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"⚠️ No images found in: {INPUT_FOLDER}")
        return 0, 0

    print(f"🚀 Processing {len(files)} images (Flat Mode)...")
    
    total_processed = 0
    total_censored = 0
    
    for filename in tqdm(files, desc="Censoring", unit="img", ncols=80):
        in_path = os.path.join(INPUT_FOLDER, filename)
        # Add _censored suffix before extension
        name_without_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]
        out_filename = f"{name_without_ext}_censored{ext}"
        out_path = os.path.join(OUTPUT_FOLDER, out_filename)
        
        success, count = process_single_image(detector, in_path, out_path)
        if success:
            total_processed += 1
            total_censored += count

    return total_processed, total_censored

def process_recursive_mode(detector):
    """
    Recursive mode: Preserve folder structure with _censored suffix on folders.
    """
    # First, count total images for progress bar
    total_images = 0
    for root, dirs, files in os.walk(INPUT_FOLDER):
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total_images += len(image_files)
    
    if total_images == 0:
        print(f"⚠️ No images found in subdirectories")
        return 0, 0
    
    print(f"🚀 Processing {total_images} images across folders (Recursive Mode)...")
    
    total_processed = 0
    total_censored = 0
    
    # Create progress bar
    with tqdm(total=total_images, desc="Censoring", unit="img", ncols=80) as pbar:
        # Walk through all subdirectories in input folder
        for root, dirs, files in os.walk(INPUT_FOLDER):
            # Calculate relative path from input folder
            rel_path = os.path.relpath(root, INPUT_FOLDER)
            
            # Skip if we're at the root level (no subdirectories to process)
            if rel_path == '.':
                continue
            
            # Split the relative path to add _censored suffix to the top-level folder
            path_parts = rel_path.split(os.sep)
            if len(path_parts) > 0:
                # Add _censored suffix to the top-level folder only
                path_parts[0] = path_parts[0] + '_censored'
            
            # Reconstruct the output path
            output_rel_path = os.sep.join(path_parts)
            output_dir = os.path.join(OUTPUT_FOLDER, output_rel_path)
            
            # Create output directory structure
            os.makedirs(output_dir, exist_ok=True)
            
            # Process all image files in this directory
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for filename in image_files:
                in_path = os.path.join(root, filename)
                # Add _censored suffix to filename before extension
                name_without_ext = os.path.splitext(filename)[0]
                ext = os.path.splitext(filename)[1]
                out_filename = f"{name_without_ext}_censored{ext}"
                out_path = os.path.join(output_dir, out_filename)
                
                success, count = process_single_image(detector, in_path, out_path)
                if success:
                    total_processed += 1
                    total_censored += count
                pbar.update(1)
    
    return total_processed, total_censored

def main():
    print("--- 🔞 Aggressive NudeNet Censor Tool ---")
    print("⚡ AGGRESSIVE MODE: Low threshold (8%), Large padding (70px)")
    
    # Auto-create folders if they don't exist
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"⚠️ Created input folder: {INPUT_FOLDER}")
        print("👉 Please put your images in there and run this again.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print("⏳ Loading NudeNet AI Model (This might take a moment)...")
    detector = NudeDetector()
    print("✅ Model loaded!")

    # Auto-detect mode
    mode = detect_mode(INPUT_FOLDER)
    print(f"📂 Mode detected: {mode.upper()}")
    
    # Process based on detected mode
    if mode == 'flat':
        processed, censored = process_flat_mode(detector)
    else:  # recursive
        processed, censored = process_recursive_mode(detector)
    
    if processed > 0:
        print(f"\n✨ SUCCESS!")
        print(f"   📊 Images processed: {processed}")
        print(f"   🔒 Regions censored: {censored}")
        print(f"   📁 Output: censor_data/output/")
        print(f"\n⚠️  IMPORTANT: Manually review images - NudeNet may miss some on anime!")
        print(f"   Detection rate on anime: ~10-20%")
    else:
        print(f"\n⚠️ No images were processed.")

if __name__ == "__main__":
    main()