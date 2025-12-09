import os
import csv
import datetime
import random
import hashlib
from PIL import Image
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
# Note: No API_KEY needed for this script! 
LINK_URL = "https://www.anione.me/en?ref_code=DailyWaifu"
IMAGES_FOLDER = "images/waifu"           # <--- UPDATED: Dedicated folder for safety
OUTPUT_CSV = "waifu_data/outputs/postpone_upload_waifu.csv" # Different output name
SEQUENCE_FILE = "waifu_data/.sequence_id"     # Unique tracker
DATE_TRACKER_FILE = "waifu_data/.last_date"   # Unique tracker
PLATFORM_PREFIX = "twitter_waifu"        # Unique prefix so it doesn't touch Makima files

# Account Handle
ACCOUNT_HANDLE = "WaifuAnimeAI"

# Schedule Settings
# Starts specifically on Dec 9, 2025 as requested
DEFAULT_START_DATE = datetime.datetime(2025, 12, 9) 

# The 4 "Golden Hours" for Global Reach (SGT)
TARGET_HOURS = [7, 13, 19, 23] 

# Jitter Settings
JITTER_MINUTES_MIN = -25 
JITTER_MINUTES_MAX = 25  

# Optimization Settings
TARGET_WIDTH = 1080

# --- GLOBAL EMOJI BANK (Hearts Only) ---
# Picked randomly for every post
EMOJI_BANK = [
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", 
    "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", 
    "😍", "🥰", "😻", "❣️", "🫶"
]

# --- CHARACTER DATABASE ---
CHARACTER_DB = {
    "a18":      {"name": "Android 18", "tags": "#Android18 #DragonBallZ #人造人間18号"},
    "akeno":    {"name": "Akeno", "tags": "#AkenoHimejima #HighSchoolDxD #姫島朱乃"},
    "albedo":   {"name": "Albedo", "tags": "#Albedo #Overlord #アルベド"},
    "annie":    {"name": "Annie", "tags": "#AnnieLeonhart #AttackOnTitan #アニ・レオンハート"},
    "asuka":    {"name": "Asuka", "tags": "#AsukaLangley #Evangelion #アスカ"},
    "ayaka":    {"name": "Ayaka", "tags": "#KamisatoAyaka #GenshinImpact #神里綾華"},
    "boa":      {"name": "Boa Hancock", "tags": "#BoaHancock #OnePiece #ボア・ハンコック"},
    "bocchi":   {"name": "Bocchi", "tags": "#HitoriGotoh #BocchiTheRock #後藤ひとり"},
    "bulma":    {"name": "Bulma", "tags": "#Bulma #DragonBall #ブルマ"},
    "chichi":   {"name": "Chi-Chi", "tags": "#ChiChi #DragonBall #チチ"},
    "chizuru":  {"name": "Chizuru", "tags": "#ChizuruMizuhara #RentAGirlfriend #水原千鶴"},
    "darkness": {"name": "Darkness", "tags": "#Darkness #Konosuba #ダクネス"},
    "erza":     {"name": "Erza", "tags": "#ErzaScarlet #FairyTail #エルザ・スカーレット"},
    "freya":    {"name": "Freya", "tags": "#Freya #DanMachi #フレイヤ"},
    "furina":   {"name": "Furina", "tags": "#Furina #GenshinImpact #フリーナ"},
    "ganyu":    {"name": "Ganyu", "tags": "#Ganyu #GenshinImpact #甘雨"},
    "hutao":    {"name": "Hu Tao", "tags": "#HuTao #GenshinImpact #胡桃"},
    "kafka":    {"name": "Kafka", "tags": "#Kafka #HonkaiStarRail #カフカ"},
    "keqing":   {"name": "Keqing", "tags": "#Keqing #GenshinImpact #刻晴"},
    "koneko":   {"name": "Koneko", "tags": "#KonekoToujou #HighSchoolDxD #塔城小猫"},
    "krista":   {"name": "Krista", "tags": "#KristaLenz #AttackOnTitan #クリスタ・レンズ"},
    "kurumi":   {"name": "Kurumi", "tags": "#KurumiTokisaki #DateALive #時崎狂三"},
    "lumine":   {"name": "Lumine", "tags": "#Lumine #GenshinImpact #蛍"},
    "mai":      {"name": "Mai", "tags": "#MaiSakurajima #BunnyGirlSenpai #桜島麻衣"},
    "makima":   {"name": "Makima", "tags": "#Makima #ChainsawMan #マキマ"},
    "marin":    {"name": "Marin", "tags": "#MarinKitagawa #DressUpDarling #喜多川海夢"},
    "mikasa":   {"name": "Mikasa", "tags": "#MikasaAckerman #AttackOnTitan #ミカサ"},
    "miku":     {"name": "Miku", "tags": "#MikuNakano #QuintessentialQuintuplets #中野三玖"},
    "mimosa":   {"name": "Mimosa", "tags": "#MimosaVermillion #BlackClover #ミモザ"},
    "mitsuri":  {"name": "Mitsuri", "tags": "#MitsuriKanroji #DemonSlayer #甘露寺蜜璃"},
    "miyabi":   {"name": "Miyabi", "tags": "#HoshimiMiyabi #ZZZ #星見雅"},
    "momo":     {"name": "Momo", "tags": "#MomoYaoyorozu #MHA #八百万百"},
    "mona":     {"name": "Mona", "tags": "#MonaMegistus #GenshinImpact #モナ"},
    "nami":     {"name": "Nami", "tags": "#Nami #OnePiece #ナミ"},
    "narberal": {"name": "Narberal", "tags": "#NarberalGamma #Overlord #ナーベラル・ガンマ"},
    "navia":    {"name": "Navia", "tags": "#Navia #GenshinImpact #ナヴィア"},
    "noelle":   {"name": "Noelle", "tags": "#NoelleSilva #BlackClover #ノエル"},
    "orihime":  {"name": "Orihime", "tags": "#OrihimeInoue #Bleach #井上織姫"},
    "raiden":   {"name": "Raiden", "tags": "#RaidenShogun #GenshinImpact #雷電将軍"},
    "rias":     {"name": "Rias", "tags": "#RiasGremory #HighSchoolDxD #リアス・グレモリー"},
    "rukia":    {"name": "Rukia", "tags": "#RukiaKuchiki #Bleach #朽木ルキア"},
    "sakura":   {"name": "Sakura", "tags": "#SakuraHaruno #Naruto #春野サクラ"},
    "shenhe":   {"name": "Shenhe", "tags": "#Shenhe #GenshinImpact #申鶴"},
    "shinobu":  {"name": "Shinobu", "tags": "#ShinobuKocho #DemonSlayer #胡蝶しのぶ"},
    "stelle":   {"name": "Stelle", "tags": "#Stelle #HonkaiStarRail #星"},
    "tamaki":   {"name": "Tamaki", "tags": "#TamakiKotatsu #FireForce #環古達"},
    "tohka":    {"name": "Tohka", "tags": "#YatogamiTohka #DateALive #夜刀神十香"},
    "tsunade":  {"name": "Tsunade", "tags": "#Tsunade #Naruto #綱手"},
    "yoimiya":  {"name": "Yoimiya", "tags": "#Yoimiya #GenshinImpact #宵宮"},
    "yor":      {"name": "Yor", "tags": "#YorForger #SpyxFamily #ヨル"},
    "yuuka":    {"name": "Yuuka", "tags": "#YuukaHayase #BlueArchive #早瀬ユウカ"},
    "zerotwo":  {"name": "Zero Two", "tags": "#ZeroTwo #DarlingInTheFranxx #ゼロツー"},
    "default":  {"name": "Waifu", "tags": "#AnimeArt #AIArt #Waifu"}
}

# --- TRACKING FUNCTIONS ---

def get_next_sequence_number():
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
                last_iso = f.read().strip()
                last_dt = datetime.datetime.fromisoformat(last_iso)
                
                candidates = []
                base_day = last_dt.replace(minute=0, second=0, microsecond=0)
                
                for d in [0, 1]:
                    day_ref = base_day + datetime.timedelta(days=d)
                    for h in TARGET_HOURS:
                        slot = day_ref.replace(hour=h)
                        if slot > last_dt:
                            candidates.append(slot)
                if candidates: return candidates[0]
        except: pass

    return DEFAULT_START_DATE.replace(hour=TARGET_HOURS[0], minute=0, second=0, microsecond=0)

def save_last_schedule(date_obj):
    with open(DATE_TRACKER_FILE, "w") as f:
        f.write(date_obj.isoformat())

def detect_character(filename):
    lower_name = filename.lower()
    for key in CHARACTER_DB:
        if key in lower_name and key != "default":
            return CHARACTER_DB[key]
    return CHARACTER_DB["default"]

# --- UTILS ---

def get_image_hash(image_path):
    with open(image_path, "rb") as f: return hashlib.md5(f.read()).hexdigest()

def force_hash_wash_image(image_path):
    """
    FORCED HASH WASHING:
    Always converts to JPG regardless of size to ensure new hash.
    Also handles resizing if larger than target width.
    """
    print(f"   🎨 Hash-Washing (Converting to JPG): {os.path.basename(image_path)}...")
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            
            # Resize only if width is too large
            if img.width > TARGET_WIDTH:
                aspect_ratio = img.height / img.width
                new_height = int(TARGET_WIDTH * aspect_ratio)
                img = img.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
            
            # Save as optimized JPEG (Changing format = New Hash)
            new_path = os.path.splitext(image_path)[0] + ".jpg"
            img.save(new_path, "JPEG", quality=90, optimize=True)
            
        # Delete original if it was different
        if new_path != image_path: 
            os.remove(image_path)
            
        return new_path
    except Exception as e:
        print(f"   ❌ Error hash-washing image: {e}")
        return image_path

def rename_and_prepare_files():
    start_index = get_next_sequence_number()
    all_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    existing_hashes = set()
    for f in all_files:
        if f.startswith(f"{PLATFORM_PREFIX}_img_"):
            existing_hashes.add(get_image_hash(os.path.join(IMAGES_FOLDER, f)))
            
    new_files = []
    for f in all_files:
        # Ignore already processed files
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
            print(f"   🚫 Skipping Duplicate: {filename}")
            continue 
        
        char_info = detect_character(filename)
        
        # New filename logic: twitter_waifu_img_001.jpg
        # (Extension will be fixed to .jpg during Hash Wash later, but we rename base first)
        ext = os.path.splitext(filename)[1]
        new_name = f"{PLATFORM_PREFIX}_img_{current_index:03d}{ext}"
        new_path = os.path.join(IMAGES_FOLDER, new_name)
        
        os.rename(full_path, new_path)
        renamed_files_list.append((new_name, current_index, char_info))
        
        existing_hashes.add(img_hash)
        current_index += 1
    
    if current_index > start_index: update_sequence_number(current_index - 1)
    return renamed_files_list

def get_next_schedule_slot(current_dt):
    next_hour = None
    for h in TARGET_HOURS:
        if h > current_dt.hour:
            next_hour = h
            break
    if next_hour is not None:
        return current_dt.replace(hour=next_hour, minute=0)
    else:
        tomorrow = current_dt + datetime.timedelta(days=1)
        return tomorrow.replace(hour=TARGET_HOURS[0], minute=0)

# --- MAIN LOOP ---

def main():
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: Folder '{IMAGES_FOLDER}' not found. Please create it!")
        return

    files_data = rename_and_prepare_files()
    
    if not files_data:
        print("No new files to process!")
        return

    current_baseline = get_start_schedule()
    
    headers = ["account", "text", "gallery", "post_at", "community", "share_with_followers", "auto_retweet", "retweet_by", "remove_after", "remove_min_likes", "thread_reply"]
    
    print("\n--- Starting Content Factory (DailyWaifuAI) ---")
    
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        
        for filename, day_number, char_info in files_data:
            full_path = os.path.join(IMAGES_FOLDER, filename)
            
            # --- FORCE HASH WASH (PNG -> JPG) ---
            final_path = force_hash_wash_image(full_path)
            final_filename = os.path.basename(final_path)
            
            # --- CAPTION GENERATION ---
            emoji = random.choice(EMOJI_BANK)
            final_caption = f"day {day_number}. {char_info['name']} {emoji}. {char_info['tags']}"
            
            print(f"   📝 {final_caption}")
            
            thread_reply_text = f"create your own unrestricted waifu here: {LINK_URL}"
            
            jitter_minutes = random.randint(JITTER_MINUTES_MIN, JITTER_MINUTES_MAX)
            actual_post_time = current_baseline + datetime.timedelta(minutes=jitter_minutes)
            post_at_str = actual_post_time.strftime("%Y-%m-%d %H:%M")
            
            print(f"      🕒 {post_at_str}")

            row = [ACCOUNT_HANDLE, final_caption, final_filename, post_at_str, "", "TRUE", "", "", "", "", thread_reply_text]
            writer.writerow(row)
            
            save_last_schedule(current_baseline)
            current_baseline = get_next_schedule_slot(current_baseline)

    print(f"\n✅ SUCCESS! Check '{OUTPUT_CSV}'.")
    print(f"📅 Next run will resume from: {current_baseline}")

if __name__ == "__main__":
    main()