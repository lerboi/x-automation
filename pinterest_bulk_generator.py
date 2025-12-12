import os
import csv
import datetime
import time
import requests
import random
import string

# --- CONFIGURATION ---
# ⚠️ CHANGE THIS to your DeviantArt Profile for safety
LINK_URL_BASE = "https://www.deviantart.com/waifudailyai" 

IMAGES_FOLDER = "images/pinterest"
OUTPUT_CSV = "pinterest_data/outputs/pinterest_bulk_upload_safe.csv"
TRACKER_FILE = "pinterest_data/.sent_log"

# Schedule Settings
PINS_PER_DAY = 3
START_DATE = datetime.datetime.now() + datetime.timedelta(days=1)

# 🇺🇸 US-OPTIMIZED HOURS (UTC)
SCHEDULE_HOURS = [1, 4, 13] 

# --- SEO BOARD MAPPING ---
BOARD_MAP = {
    "makima": "Chainsaw Man: Makima & Power",
    "ayaka": "Genshin Impact: Wallpapers & Art",
    "citlali": "Genshin Impact: Wallpapers & Art",
    "furina": "Genshin Impact: Wallpapers & Art",
    "hutao": "Genshin Impact: Wallpapers & Art",
    "keqing": "Genshin Impact: Wallpapers & Art",
    "mona": "Genshin Impact: Wallpapers & Art",
    "noelle": "Genshin Impact: Wallpapers & Art",
    "akane": "Oshi no Ko: Ruby, Akane & Kana",
    "kana": "Oshi no Ko: Ruby, Akane & Kana",
    "ruby": "Oshi no Ko: Ruby, Akane & Kana",
    "hinata": "Naruto Shippuden: Hinata & Sakura",
    "sakura": "Naruto Shippuden: Hinata & Sakura",
    "zerotwo": "Zero Two | Darling in the Franxx",
    "yor": "Spy x Family: Yor Forger Aesthetic",
    "shinobu": "Demon Slayer: Shinobu & Art",
    "boa": "One Piece: Boa Hancock",
    "rukia": "Bleach Anime: Rukia & Art",
    "mikasa": "Attack on Titan: Mikasa Aesthetic",
    "fern": "Frieren: Beyond Journey's End",
    "mai": "Anime Waifu Wallpapers 4K",
    "marin": "Anime Waifu Wallpapers 4K",
    "chizuru": "Anime Waifu Wallpapers 4K",
    "default": "Anime Waifu Wallpapers 4K"
}

# --- SAFE TITLE TEMPLATES (Sanitized for Pinterest) ---
# Removed "Unrestricted", "Waifu", "NSFW" keywords to prevent shadowbans.
TITLE_TEMPLATES = [
    "{char} 4K Wallpaper | Stunning AI Art",
    "{char} Aesthetic Art | High Quality",
    "Best {char} Generated Art (4K)",
    "{char} Portrait | Anime Waifu Aesthetic",
    "{char} Wallpaper | {series} Art",
    "Stunning {char} Fan Art | AI Gen",
    "{char} Best PFP | High Res",
    "Beautiful {char} Wallpaper (4K)",
    "{char} {series} | Fan Art",
    "Cute {char} Profile Picture | HD",
    "{char} Digital Art | High Quality",
    "Best Art of {char} | {series}",
    "{char} Desktop Wallpaper | 4K Anime",
    "{char} Mobile Wallpaper | Aesthetic",
    "Daily {char} Art | Generated",
    "{char} Fanart Edition | High Quality",
    "Top Tier {char} Art | {series}",
    "{char} Concept Art | Gen Art",
    "Beautiful {char} Portrait (4K)",
    "{char} Anime Style | Aesthetic"
]

# --- FUNCTIONS ---

def get_sent_log():
    if not os.path.exists(TRACKER_FILE): return set()
    with open(TRACKER_FILE, "r") as f:
        return set(line.strip() for line in f)

def update_sent_log(filename):
    # Ensure directory exists before writing
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, "a") as f:
        f.write(f"{filename}\n")

def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    try:
        with open(file_path, "rb") as f:
            files = {"fileToUpload": f}
            data = {"reqtype": "fileupload", "userhash": ""}
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"   ❌ Catbox Error: {response.text}")
                return None
    except Exception as e:
        print(f"   ❌ Upload Exception: {e}")
        return None

def get_character_info(filename):
    lower = filename.lower()
    detected_char = "Anime Girl"
    target_board = BOARD_MAP["default"]
    
    for key, board in BOARD_MAP.items():
        if key in lower and key != "default":
            detected_char = key.title()
            target_board = board
            if key == "hutao": detected_char = "Hu Tao"
            if key == "zerotwo": detected_char = "Zero Two"
            if key == "boa": detected_char = "Boa Hancock"
            break
            
    if ":" in target_board:
        series_name = target_board.split(":")[0]
    elif "|" in target_board:
        series_name = target_board.split("|")[0].strip()
    else:
        series_name = "Anime"
        
    return detected_char, target_board, series_name

used_titles_registry = set()

def generate_unique_seo_data(char_name, series_name):
    attempts = 0
    title = ""
    while attempts < 50:
        template = random.choice(TITLE_TEMPLATES)
        title_candidate = template.format(char=char_name, series=series_name)
        if title_candidate not in used_titles_registry:
            title = title_candidate
            break
        attempts += 1
    
    if title == "":
        base = random.choice(TITLE_TEMPLATES).format(char=char_name, series=series_name)
        title = f"{base} ({random.randint(1, 999)})"
    
    used_titles_registry.add(title)
    
    # Safe Description
    desc = (f"High quality art of {char_name} from {series_name}. "
        f"Generated with Anione. "  # <--- Added Safe Mention
        f"Stunning 4K anime wallpaper... 🔗 #Anime #Art")
    
    keywords = f"anime, art, {char_name}, {series_name}, wallpaper, 4k, aesthetic, digital art, pfp"
    
    if len(title) > 100: title = title[:97] + "..."
    if len(desc) > 500: desc = desc[:497] + "..."
        
    return title, desc, keywords

def generate_unique_link():
    random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    if "?" in LINK_URL_BASE:
        return f"{LINK_URL_BASE}&v={random_id}"
    else:
        return f"{LINK_URL_BASE}?v={random_id}"

def get_schedule_slots(total_images):
    slots = []
    current = START_DATE
    days_needed = (total_images // len(SCHEDULE_HOURS)) + 2
    for _ in range(days_needed): 
        for hour in SCHEDULE_HOURS:
            slot = current.replace(hour=hour, minute=0, second=0)
            slots.append(slot)
        current += datetime.timedelta(days=1)
    return slots

def main():
    print("--- Pinterest Content Engine (Safe Root-Only Edition) ---")
    
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: Folder '{IMAGES_FOLDER}' not found.")
        return

    sent_files = get_sent_log()
    
    # --- STRICT FILTERING LOGIC ---
    new_files = []
    
    # 1. List only immediate items in the folder (No Walk)
    items = os.listdir(IMAGES_FOLDER)
    
    for item in items:
        full_path = os.path.join(IMAGES_FOLDER, item)
        
        # 2. Skip items starting with '.' (Hidden files/folders)
        if item.startswith('.'):
            continue
            
        # 3. Skip directories (Only files allowed)
        if not os.path.isfile(full_path):
            continue
            
        # 4. Check Extension
        if item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            if item not in sent_files:
                new_files.append(item)
    
    random.shuffle(new_files)

    if not new_files:
        print("✅ No new files to process!")
        return

    print(f"🚀 Found {len(new_files)} new images in root folder. Processing...")
    
    headers = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
    
    schedule_slots = get_schedule_slots(len(new_files))
    slot_index = 0
    success_count = 0

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

        for filename in new_files:
            full_path = os.path.join(IMAGES_FOLDER, filename)
            char_name, board_name, series_name = get_character_info(filename)
            
            title, desc, keywords = generate_unique_seo_data(char_name, series_name)
            unique_link = generate_unique_link()
            
            print(f"[{slot_index+1}/{len(new_files)}] {char_name}")

            image_url = upload_to_catbox(full_path)
            
            if image_url:
                post_time = schedule_slots[slot_index]
                post_time_str = post_time.strftime("%Y-%m-%dT%H:%M:%S")
                
                row = [title, image_url, board_name, "", desc, unique_link, post_time_str, keywords]
                writer.writerow(row)
                
                update_sent_log(filename)
                success_count += 1
                slot_index += 1
                time.sleep(2.5) 
            else:
                print("   ❌ Skipping file due to upload failure.")

    print(f"\n✅ DONE! Generated {success_count} Pins in '{OUTPUT_CSV}'.")
    print("👉 Upload this to Pinterest.")

if __name__ == "__main__":
    main()