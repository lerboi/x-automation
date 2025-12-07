import os
import csv
import base64
import datetime
import time
import io
from PIL import Image
from mistralai import Mistral

# --- CONFIGURATION ---
API_KEY = os.environ.get("API_KEY")
LINK_URL = "https://www.anione.me/en"
IMAGES_FOLDER = "images"
OUTPUT_CSV = "postpone_upload.csv"

# Schedule Settings
START_DATE = datetime.datetime.now() + datetime.timedelta(days=1) # Starts tomorrow
START_HOUR = 8 # 8:00 AM
POSTS_PER_DAY = 2
HOURS_BETWEEN_POSTS = 12

# Optimization Settings
MAX_FILE_SIZE_MB = 4.5
TARGET_WIDTH = 1080

# AI Persona
CHARACTER_NAME = "Makima"
SYSTEM_PROMPT = f"""
You are the archivist for a 'Daily {CHARACTER_NAME}' fan page.
1. Write a short, engaging caption (under 200 chars) describing the image.
2. Speak in the THIRD PERSON (e.g., "She looks...", "{CHARACTER_NAME} is...").
3. Do NOT include any URLs or links in the caption.
4. Include exactly 3 hashtags (e.g. #{CHARACTER_NAME} #ChainsawMan #AIArt).
5. Output ONLY the caption and hashtags.
"""

def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def optimize_image(image_path):
    """
    Checks if image > 4.5MB. If so, resizes to 1080px width and compresses.
    Overwrites the original file if optimization occurs.
    """
    if get_file_size_mb(image_path) < MAX_FILE_SIZE_MB:
        return # File is small enough, skip

    print(f"   ⚠️ Optimizing large file: {os.path.basename(image_path)}...")
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB (in case of RGBA PNGs which can't be saved as JPEG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Calculate new height maintaining aspect ratio
            aspect_ratio = img.height / img.width
            new_height = int(TARGET_WIDTH * aspect_ratio)
            
            img = img.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
            
            # Save as optimized JPEG
            # We change extension to .jpg to ensure compression works well
            new_path = os.path.splitext(image_path)[0] + ".jpg"
            img.save(new_path, "JPEG", quality=85, optimize=True)
            
        # Remove old huge file if we changed extension
        if new_path != image_path:
            os.remove(image_path)
            
        return new_path # Return the new filename
        
    except Exception as e:
        print(f"   ❌ Error optimizing image: {e}")
        return image_path

def encode_image(image_path):
    """Encodes image to Base64 for Mistral"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def rename_and_sort_files():
    """Renames images to img_001, img_002... and returns sorted list"""
    # Grab all valid image files
    files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    files.sort() # Sort alphabetically first to keep order
    
    clean_files = []
    
    print(f"Found {len(files)} images. Renaming and preparing...")
    
    for index, filename in enumerate(files):
        old_path = os.path.join(IMAGES_FOLDER, filename)
        
        # Determine extension (might change if we optimized it, but for now keep original)
        ext = os.path.splitext(filename)[1]
        new_name = f"img_{index+1:03d}{ext}"
        new_path = os.path.join(IMAGES_FOLDER, new_name)
        
        # Rename file
        if old_path != new_path:
            os.rename(old_path, new_path)
            
        clean_files.append(new_name)
        
    return clean_files

def main():
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: Folder '{IMAGES_FOLDER}' not found. Please create it.")
        return

    # Initialize Mistral Client
    client = Mistral(api_key=API_KEY)
    
    # 1. Rename files for consistency
    files = rename_and_sort_files()
    
    # 2. Set Start Date
    current_schedule = START_DATE.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    
    # 3. CSV Headers (Matching your Postpone example)
    headers = [
        "account", "text", "gallery", "post_at", 
        "community", "share_with_followers", "auto_retweet", 
        "retweet_by", "remove_after", "remove_min_likes", "thread_reply"
    ]
    
    print("\n--- Starting Processing Loop ---")
    
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for filename in files:
            full_path = os.path.join(IMAGES_FOLDER, filename)
            
            # A. Optimization Step (Resize if > 4.5MB)
            # This might change the filename extension if converted to jpg
            final_path = optimize_image(full_path)
            final_filename = os.path.basename(final_path)
            
            print(f"Processing: {final_filename}...")
            
            try:
                # B. Generate Content
                base64_img = encode_image(final_path)
                
                chat_response = client.chat.complete(
                    model="pixtral-12b-2409",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": SYSTEM_PROMPT},
                                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}
                            ]
                        }
                    ]
                )
                
                caption = chat_response.choices[0].message.content.strip()
                
                # C. Prepare Data Rows
                post_at_str = current_schedule.strftime("%Y-%m-%d %H:%M")
                
                # The Thread Reply (Where your link goes)
                thread_reply_text = f"Create your own unrestricted {CHARACTER_NAME} here: {LINK_URL}"
                
                row = [
                    "",                 # account (Select in Postpone)
                    caption,            # text
                    final_filename,     # gallery
                    post_at_str,        # post_at
                    "",                 # community
                    "TRUE",             # share_with_followers
                    "",                 # auto_retweet
                    "",                 # retweet_by
                    "",                 # remove_after
                    "",                 # remove_min_likes
                    thread_reply_text   # thread_reply
                ]
                
                writer.writerow(row)
                
                # D. Increment Schedule
                current_schedule += datetime.timedelta(hours=HOURS_BETWEEN_POSTS)
                
                # Small sleep to be nice to the API
                time.sleep(1)

            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")

    print(f"\n✅ SUCCESS! Generated '{OUTPUT_CSV}'.")
    print(f"1. Open Postpone > Bulk Import.")
    print(f"2. Upload ALL files from the '{IMAGES_FOLDER}' folder to Postpone.")
    print(f"3. Upload '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    main()