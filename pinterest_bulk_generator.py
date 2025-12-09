import os
import csv
import datetime
import time
import requests
import random
import string

# --- CONFIGURATION ---
LINK_URL_BASE = "https://www.anione.me/en?ref_code=pinterest"
IMAGES_FOLDER = "pinterest_images"
OUTPUT_CSV = "pinterest_bulk_upload_final.csv"
TRACKER_FILE = ".pinterest_sent_log"

# Schedule Settings
PINS_PER_DAY = 3
START_DATE = datetime.datetime.now() + datetime.timedelta(days=1)

# 🇺🇸 US-OPTIMIZED HOURS (UTC)
# Pinterest reads CSV times as UTC. We want US Prime Time.
# 01:00 UTC = 8:00 PM EST (New York)
# 04:00 UTC = 8:00 PM PST (Los Angeles)
# 13:00 UTC = 8:00 AM EST (New York Morning)
SCHEDULE_HOURS = [1, 4, 13] 

# --- SEO BOARD MAPPING ---
BOARD_MAP = {
    # Genshin Impact
    "ayaka": "Genshin Impact: Wallpapers & Art",
    "citlali": "Genshin Impact: Wallpapers & Art",
    "furina": "Genshin Impact: Wallpapers & Art",
    "hutao": "Genshin Impact: Wallpapers & Art",
    "keqing": "Genshin Impact: Wallpapers & Art",
    "mona": "Genshin Impact: Wallpapers & Art",
    "noelle": "Genshin Impact: Wallpapers & Art",
    
    # Oshi no Ko
    "akane": "Oshi no Ko: Ruby, Akane & Kana",
    "kana": "Oshi no Ko: Ruby, Akane & Kana",
    "ruby": "Oshi no Ko: Ruby, Akane & Kana",
    
    # Naruto
    "hinata": "Naruto Shippuden: Hinata & Sakura",
    "sakura": "Naruto Shippuden: Hinata & Sakura",
    
    # Specific Character Boards
    "zerotwo": "Zero Two | Darling in the Franxx",
    "yor": "Spy x Family: Yor Forger Aesthetic",
    "shinobu": "Demon Slayer: Shinobu & Art",
    "boa": "One Piece: Boa Hancock",
    "rukia": "Bleach Anime: Rukia & Art",
    "mikasa": "Attack on Titan: Mikasa Aesthetic",
    "fern": "Frieren: Beyond Journey's End",
    
    # The "RomCom" Group
    "mai": "Anime Waifu Wallpapers 4K",
    "marin": "Anime Waifu Wallpapers 4K",
    "chizuru": "Anime Waifu Wallpapers 4K",
    
    # Fallback
    "default": "Anime Waifu Wallpapers 4K"
}

# --- EXPANDED TITLE TEMPLATES (20+ Options) ---
TITLE_TEMPLATES = [
    "{char} 4K Wallpaper | Unrestricted AI Art",
    "{char} Aesthetic Art | High Quality",
    "Best {char} AI Generated Art (4K)",
    "{char} Portrait | Anime Waifu Aesthetic",
    "{char} Wallpaper | {series} Art",
    "Unrestricted {char} Fan Art | AI Gen",
    "{char} Best PFP | High Res",
    "Stunning {char} Wallpaper (4K)",
    "{char} {series} | AI Fan Art",
    "Cute {char} Profile Picture | HD",
    "{char} Digital Art | Unrestricted",
    "Best AI Art of {char} | {series}",
    "{char} Desktop Wallpaper | 4K Anime",
    "{char} Mobile Wallpaper | Aesthetic",
    "Daily {char} Art | AI Generated",
    "{char} Waifu Edition | High Quality",
    "Top Tier {char} Art | {series}",
    "{char} Concept Art | AI Gen",
    "Beautiful {char} Portrait (4K)",
    "{char} Anime Style | Unrestricted"
]

# --- FUNCTIONS ---

def get_sent_log():
    if not os.path.exists(TRACKER_FILE): return set()
    with open(TRACKER_FILE, "r") as f:
        return set(line.strip() for line in f)

def update_sent_log(filename):
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

# Global set to track used titles in this run
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
    
    desc = (f"High quality, unrestricted AI art of {char_name} from {series_name}. "
            f"Stunning 4K anime wallpaper, aesthetic pfp, and character design. "
            f"Generate your own anime characters here. 🔗 #AIArt #Anime #Waifu #{char_name.replace(' ', '')}")
    
    keywords = f"anime, ai art, waifu, {char_name}, {series_name}, wallpaper, 4k, aesthetic, digital art, pfp"
    
    if len(title) > 100: title = title[:97] + "..."
    if len(desc) > 500: desc = desc[:497] + "..."
        
    return title, desc, keywords

def generate_unique_link():
    # Appends &v=RANDOM to URL to bypass spam filters
    random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{LINK_URL_BASE}&v={random_id}"

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

# --- MAIN ---

def main():
    print("--- Pinterest Content Engine (Bypass Edition) ---")
    
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: Folder '{IMAGES_FOLDER}' not found.")
        return

    sent_files = get_sent_log()
    all_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    new_files = [f for f in all_files if f not in sent_files]
    random.shuffle(new_files)

    if not new_files:
        print("✅ No new files to process!")
        return

    print(f"🚀 Found {len(new_files)} new images. Processing...")
    
    headers = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
    
    schedule_slots = get_schedule_slots(len(new_files))
    slot_index = 0
    success_count = 0

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

        for filename in new_files:
            full_path = os.path.join(IMAGES_FOLDER, filename)
            char_name, board_name, series_name = get_character_info(filename)
            
            title, desc, keywords = generate_unique_seo_data(char_name, series_name)
            
            # GENERATE UNIQUE LINK FOR EVERY PIN
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

    print(f"\n✅ DONE! Generated {success_count} unique Pins in '{OUTPUT_CSV}'.")
    print("👉 Upload this file. The 'Duplicate Pin Link' error should now be resolved.")

if __name__ == "__main__":
    main()