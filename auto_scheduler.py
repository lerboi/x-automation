import os
import csv
import base64
import datetime
import time
import random
import hashlib
from PIL import Image
from mistralai import Mistral
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.environ.get("API_KEY") 
LINK_URL = "https://www.anione.me/en?ref_code=DailyMakima"
IMAGES_FOLDER = "images"
OUTPUT_CSV = "postpone_upload.csv"
SEQUENCE_FILE = ".sequence_id"      
DATE_TRACKER_FILE = ".last_date"    
PLATFORM_PREFIX = "twitter"

# Account Name (No '@')
ACCOUNT_HANDLE = "DailyMakimaAI"

# Schedule Settings
DEFAULT_START_DATE = datetime.datetime(2025, 12, 10) 
START_HOUR = 8 
POSTS_PER_DAY = 2
HOURS_BETWEEN_POSTS = 12

# Jitter Settings
JITTER_MINUTES_MIN = -25 
JITTER_MINUTES_MAX = 25  

# Optimization Settings
MAX_FILE_SIZE_MB = 4.5
TARGET_WIDTH = 1080

# --- HASHTAG STRATEGY ---
TAGS_CHARACTER = ["#Makima", "#マキマ", "#MakimaChainsawMan"] 
TAGS_SERIES = ["#ChainsawMan", "#CSM", "#チェンソーマン"]
TAGS_NICHE = ["#AIArt", "#AIAnime", "#Waifu"]

# --- PERSONA ---
SYSTEM_PROMPT = """
You are a minimalist aesthetic curator for a Makima art page.
Your task: Describe the image with a very simple vibe and an emoji.
Rules:
1. STRICTLY 1 or 2 words maximum.
2. Lowercase text ONLY. No periods.
3. Add exactly ONE matching emoji at the end.
4. Do NOT use generic words like "image" or "picture".
5. Examples:
   - "office siren 🚨"
   - "control 🐕"
   - "listening 🎧"
   - "morning ☕"
   - "night shift 🌙"
   - "gaze 👁️"
   - "red 🩸"
6. Output ONLY the text and emoji.
"""

# --- ROBUST TRACKING FUNCTIONS ---

def get_next_sequence_number():
    """FAIL-SAFE: Checks both the file AND the actual folder."""
    file_seq = 1
    if os.path.exists(SEQUENCE_FILE):
        try:
            with open(SEQUENCE_FILE, "r") as f:
                file_seq = int(f.read().strip()) + 1
        except: pass

    folder_max = 0
    try:
        existing_files = [f for f in os.listdir(IMAGES_FOLDER) if f.startswith(f"{PLATFORM_PREFIX}_img_")]
        for f in existing_files:
            try:
                num_part = f.split("_img_")[1].split(".")[0]
                num = int(num_part)
                if num > folder_max: folder_max = num
            except: pass
    except: pass
    
    final_seq = max(file_seq, folder_max + 1)
    if final_seq > file_seq: update_sequence_number(final_seq - 1)
    return final_seq

def update_sequence_number(last_number):
    with open(SEQUENCE_FILE, "w") as f: f.write(str(last_number))

def get_start_schedule():
    if os.path.exists(DATE_TRACKER_FILE):
        try:
            with open(DATE_TRACKER_FILE, "r") as f:
                last_date = datetime.datetime.fromisoformat(f.read().strip())
                return last_date + datetime.timedelta(hours=HOURS_BETWEEN_POSTS)
        except: pass
    return DEFAULT_START_DATE.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)

def save_last_schedule(date_obj):
    with open(DATE_TRACKER_FILE, "w") as f:
        f.write(date_obj.isoformat())

# --- UTILS ---

def get_image_hash(image_path):
    with open(image_path, "rb") as f: return hashlib.md5(f.read()).hexdigest()

def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def optimize_image(image_path):
    if get_file_size_mb(image_path) < MAX_FILE_SIZE_MB: return image_path 
    print(f"   ⚠️ Optimizing large file: {os.path.basename(image_path)}...")
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            aspect_ratio = img.height / img.width
            new_height = int(TARGET_WIDTH * aspect_ratio)
            img = img.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
            new_path = os.path.splitext(image_path)[0] + ".jpg"
            img.save(new_path, "JPEG", quality=85, optimize=True)
        if new_path != image_path: os.remove(image_path)
        return new_path
    except Exception as e:
        print(f"   ❌ Error optimizing image: {e}")
        return image_path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def rename_and_prepare_files():
    start_index = get_next_sequence_number()
    all_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    existing_hashes = set()
    for f in all_files:
        if f.startswith(f"{PLATFORM_PREFIX}_img_"):
            existing_hashes.add(get_image_hash(os.path.join(IMAGES_FOLDER, f)))
            
    new_files = []
    
    for f in all_files:
        if not f.startswith(f"{PLATFORM_PREFIX}_img_"):
            new_files.append(f)

    random.shuffle(new_files)
    
    renamed_files_list = []
    current_index = start_index
    print(f"🔄 Starting sequence from: Day {current_index}")
    
    for filename in new_files:
        full_path = os.path.join(IMAGES_FOLDER, filename)
        
        img_hash = get_image_hash(full_path)
        if img_hash in existing_hashes:
            print(f"   🚫 Skipping Duplicate Image: {filename}")
            continue 
        
        ext = os.path.splitext(filename)[1]
        new_name = f"{PLATFORM_PREFIX}_img_{current_index:03d}{ext}"
        new_path = os.path.join(IMAGES_FOLDER, new_name)
        
        os.rename(full_path, new_path)
        renamed_files_list.append((new_name, current_index))
        existing_hashes.add(img_hash)
        current_index += 1
    
    if current_index > start_index: update_sequence_number(current_index - 1)
    return renamed_files_list

def generate_smart_hashtags():
    return f"{random.choice(TAGS_CHARACTER)} {random.choice(TAGS_SERIES)} {random.choice(TAGS_NICHE)}"

# --- MAIN LOOP ---

def main():
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: Folder '{IMAGES_FOLDER}' not found.")
        return

    client = Mistral(api_key=API_KEY)
    
    files_with_days = rename_and_prepare_files()
    
    if not files_with_days:
        print("No new files to process!")
        return

    current_baseline = get_start_schedule()
    recent_captions = [] 
    headers = ["account", "text", "gallery", "post_at", "community", "share_with_followers", "auto_retweet", "retweet_by", "remove_after", "remove_min_likes", "thread_reply"]
    
    print("\n--- Starting Content Factory ---")
    
    # 1. UTF-8-SIG for correct Emoji display
    # 2. QUOTE_MINIMAL keeps the file cleaner (closer to the example), quoting only when necessary
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        
        for filename, day_number in files_with_days:
            full_path = os.path.join(IMAGES_FOLDER, filename)
            final_path = optimize_image(full_path)
            final_filename = os.path.basename(final_path)
            print(f"Processing Day {day_number}: {final_filename}...")
            
            try:
                base64_img = encode_image(final_path)
                caption_text = "makima 🩸" 
                attempts = 0
                
                while attempts < 3:
                    try:
                        chat_response = client.chat.complete(
                            model="pixtral-12b-2409",
                            messages=[{"role": "user", "content": [{"type": "text", "text": SYSTEM_PROMPT}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_img}"}]}]
                        )
                        raw = chat_response.choices[0].message.content.strip().lower().replace(".", "").replace('"', '')
                        
                        if raw in recent_captions:
                            print(f"   ⚠️ Duplicate caption '{raw}'. shuffling...")
                            attempts += 1
                            continue 
                        else:
                            caption_text = raw
                            break
                    except Exception as api_error:
                        print(f"   ⚠️ API Error ({api_error}). Retrying in 5s...")
                        time.sleep(5)
                        attempts += 1
                
                recent_captions.append(caption_text)
                if len(recent_captions) > 5: recent_captions.pop(0)

                smart_hashtags = generate_smart_hashtags()
                
                # --- FLATTENED CAPTION ---
                # Replaced "\n\n" with a simple space to ensure 1 line per post
                final_caption = f"day {day_number}. {caption_text}. {smart_hashtags}"
                
                print(f"   📝 Caption: {final_caption}")
                
                # Removed newlines from the link reply as well
                thread_reply_text = f"create your own unrestricted makima here: {LINK_URL}"
                
                jitter_minutes = random.randint(JITTER_MINUTES_MIN, JITTER_MINUTES_MAX)
                actual_post_time = current_baseline + datetime.timedelta(minutes=jitter_minutes)
                post_at_str = actual_post_time.strftime("%Y-%m-%d %H:%M")
                
                row = [ACCOUNT_HANDLE, final_caption, final_filename, post_at_str, "", "TRUE", "", "", "", "", thread_reply_text]
                writer.writerow(row)
                
                save_last_schedule(current_baseline)
                current_baseline += datetime.timedelta(hours=HOURS_BETWEEN_POSTS)
                time.sleep(1.5)

            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")

    print(f"\n✅ SUCCESS! Check '{OUTPUT_CSV}'.")
    print(f"📅 Next run will resume from: {current_baseline}")

if __name__ == "__main__":
    main()