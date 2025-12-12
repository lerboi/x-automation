import os
import shutil
import random
import datetime
from PIL import Image

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_DIR = os.path.join(BASE_DIR, "deviantart_workflow")
INPUT_SAFE = os.path.join(WORKFLOW_DIR, "1_Raw_Safe")
INPUT_MATURE = os.path.join(WORKFLOW_DIR, "1_Raw_Mature")
OUTPUT_ROOT = os.path.join(WORKFLOW_DIR, "3_Ready_To_Upload")
ARCHIVE_ROOT = os.path.join(WORKFLOW_DIR, "4_Archived")
WATERMARK_FILE = os.path.join(BASE_DIR, "watermark.png")

# --- SETTINGS (5 Safe / 1 Mature Strategy) ---
SAFE_PER_DAY = 2
MATURE_PER_DAY = 1
DAYS = ["01_Monday", "02_Tuesday", "03_Wednesday", "04_Thursday", "05_Friday", "06_Saturday", "07_Sunday"]

# --- SCHEDULE TIMES (US Optimized - Converted to SGT) ---
# 5 Safe Slots
SAFE_TIMES = ["08:00", "22:00"] 
# 1 Mature Slot (The "Money" Slot)
MATURE_TIMES = ["11:00"]

# --- EMOJI ID POOL ---
EMOJI_IDS = [
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", 
    "💖", "💗", "💓", "💞", "💕", "💘", "💝", "💟", 
    "🔥", "✨", "💫", "⭐", "🌟", "🌹", "🌺", "🌸"
]

# --- WATERMARK SETTINGS (Bottom Left) ---
LOGO_SCALE = 0.45       
OPACITY = 215           
PADDING_X = 15          
PADDING_Y = 10          

# --- TRAFFIC OPTIMIZED TAG DATABASE (Cleaned based on your files) ---
TAG_DB = {
    # --- DRAGON BALL ---
    "android18": "#Android18 #C18 #Lazuli #DragonBallZ #DBZ #DragonBallSuper #Android18Fanart #Waifu #AIArt",
    "bulma": "#Bulma #BulmaBriefs #DragonBall #DBZ #DragonBallSuper #BulmaFanart #AnimeGirl #AIArt",
    "chichi": "#ChiChi #DragonBall #DBZ #Milk #GokuWife #ChiChiFanart #AnimeWaifu #AIArt",
    
    # --- NARUTO ---
    "hinata": "#HinataHyuga #Hinata #NarutoShippuden #Boruto #Byakugan #HinataFanart #NarutoWaifu #AIArt",
    "sakura": "#SakuraHaruno #SakuraUchiha #NarutoShippuden #Boruto #Kunoichi #SakuraFanart #AIArt",
    "ino": "#InoYamanaka #Ino #NarutoShippuden #YamanakaClan #InoFanart #AnimeGirl #AIArt",
    "tsunade": "#Tsunade #LadyTsunade #NarutoShippuden #Hokage #Sannin #106 #TsunadeFanart #AIArt",
    
    # --- ONE PIECE ---
    "nami": "#Nami #CatBurglarNami #OnePiece #StrawHatPirates #NamiOnePiece #NamiFanart #AnimeGirl #AIArt",
    "boa": "#BoaHancock #PirateEmpress #OnePiece #Boa #Hancock #SnakePrincess #BoaHancockFanart #Waifu #AIArt",
    
    # --- GENSHIN IMPACT ---
    "ayaka": "#KamisatoAyaka #Ayaka #GenshinImpact #Inazuma #Cryo #AyakaFanart #GenshinWaifu #AIArt",
    "furina": "#Furina #Focalors #GenshinImpact #Fontaine #HydroArchon #FurinaFanart #GenshinImpactFanart #AIArt",
    "ganyu": "#Ganyu #GenshinImpact #Liyue #Cryo #Cocoatgoat #GanyuFanart #GenshinWaifu #AIArt",
    "hutao": "#HuTao #GenshinImpact #Liyue #Pyro #WangshengFuneralParlor #HuTaoFanart #GenshinImpact #AIArt",
    "keqing": "#Keqing #GenshinImpact #Liyue #Electro #Yuheng #KeqingFanart #GenshinWaifu #AIArt",
    "noelle": "#Noelle #GenshinImpact #Mondstadt #Geo #MaidKnight #NoelleFanart #GenshinMaid #AIArt",
    
    # --- ZZZ ---
    "ellen": "#EllenJoe #ZenlessZoneZero #ZZZ #Ellen #SharkGirl #VictoriaHousekeeping #EllenJoeFanart #AIArt",
    "jane": "#JaneDoe #ZenlessZoneZero #ZZZ #JaneDoeZZZ #RatThiren #JaneDoeFanart #ZZZWaifu #AIArt",
    "miyabi": "#HoshimiMiyabi #ZenlessZoneZero #ZZZ #Miyabi #SamuraiGirl #Section6 #MiyabiFanart #AIArt",
    "nicole": "#NicoleDemara #ZenlessZoneZero #ZZZ #Nicole #CunningHares #NicoleDemaraFanart #AIArt",
    "zhuyuan": "#ZhuYuan #ZenlessZoneZero #ZZZ #PoliceGirl #PubSec #ZhuYuanFanart #ZZZFanart #AIArt",
    
    # --- NIKKE ---
    "anis": "#Anis #GoddessOfVictoryNikke #Nikke #AnisNikke #CountersSquad #AnisFanart #NikkeWaifu #AIArt",
    
    # --- CHAINSAW MAN ---
    "makima": "#Makima #ChainsawMan #CSM #ControlDevil #MakimaSan #MakimaFanart #AnimeGirl #AIArt",
    
    # --- BLEACH ---
    "orihime": "#OrihimeInoue #Bleach #Orihime #KurosakiOrihime #ArrancarArc #OrihimeFanart #BleachWaifu #AIArt",
    "rukia": "#RukiaKuchiki #Bleach #Rukia #Shinigami #SoulSociety #Bankai #RukiaFanart #AIArt",
    
    # --- SPY X FAMILY ---
    "yor": "#YorForger #YorBriar #SpyxFamily #ThornPrincess #Assassin #YorFanart #SpyXFamilyFanart #Waifu #AIArt",
    
    # --- AOT ---
    "annie": "#AnnieLeonhart #AttackOnTitan #AOT #ShingekiNoKyojin #FemaleTitan #AnnieFanart #AIArt",
    "krista": "#HistoriaReiss #KristaLenz #AttackOnTitan #AOT #QueenHistoria #HistoriaFanart #AIArt",
    "mikasa": "#MikasaAckerman #AttackOnTitan #AOT #Mikasa #ShingekiNoKyojin #MikasaFanart #Ackerman #AIArt",
    
    # --- FAIRY TAIL ---
    "erza": "#ErzaScarlet #FairyTail #Erza #Titania #RequipMagic #ErzaFanart #AnimeGirl #AIArt",
    
    # --- DEMON SLAYER ---
    "mitsuri": "#MitsuriKanroji #DemonSlayer #KimetsuNoYaiba #LoveHashira #MitsuriFanart #DemonSlayerWaifu #AIArt",
    "shinobu": "#ShinobuKocho #DemonSlayer #KimetsuNoYaiba #InsectHashira #ShinobuFanart #AIArt",
    
    # --- HIGH SCHOOL DXD ---
    "akeno": "#AkenoHimejima #HighSchoolDxD #Akeno #RiasPeerage #Priestess #AkenoFanart #AnimeWaifu #AIArt",
    "koneko": "#KonekoToujou #HighSchoolDxD #Koneko #Nekomata #KonekoFanart #AnimeGirl #AIArt",
    "rias": "#RiasGremory #HighSchoolDxD #Rias #Gremory #CrimsonHairedRuinPrincess #RiasFanart #AIArt",
    
    # --- DATE A LIVE ---
    "kurumi": "#KurumiTokisaki #DateALive #Kurumi #Nightmare #Spirit #TokisakiKurumi #KurumiFanart #AIArt",
    "tohka": "#TohkaYatogami #DateALive #Tohka #Princess #Spirit #YatogamiTohka #TohkaFanart #AIArt",
    
    # --- KONOSUBA ---
    "darkness": "#Darkness #Konosuba #Lalatina #Crusader #DarknessKonosuba #DarknessFanart #AnimeGirl #AIArt",
    
    # --- OVERLORD ---
    "albedo": "#Albedo #Overlord #Succubus #GuardianOverseer #AlbedoOverlord #AlbedoFanart #AnimeGirl #AIArt",
    "narberal": "#NarberalGamma #Overlord #Nabe #Pleiades #Maid #NarberalFanart #AnimeGirl #AIArt",
    
    # --- RENT A GIRLFRIEND ---
    "chizuru": "#ChizuruMizuhara #RentAGirlfriend #KanojoOkarishimasu #ChizuruIchinose #ChizuruFanart #AIArt",
    
    # --- FIRE FORCE ---
    "maki": "#MakiOze #FireForce #EnenNoShouboutai #Maki #Witch #FireSoldier #MakiFanart #AIArt",
    "tamaki": "#TamakiKotatsu #FireForce #EnenNoShouboutai #Tamaki #Nekomata #LuckyLecher #TamakiFanart #AIArt",
    
    # --- DANMACHI ---
    "haruhime": "#SanjounoHaruhime #DanMachi #Haruhime #Renard #FoxGirl #HaruhimeFanart #AnimeWaifu #AIArt",
    "hestia": "#Hestia #DanMachi #GoddessHestia #LoliKami #HestiaFanart #AnimeGirl #AIArt",
    
    # --- EMINENCE IN SHADOW ---
    "alice": "#AliceMidgar #TheEminenceInShadow #EminenceInShadow #AnimeGirl #AIArt",
    
    # --- BLACK CLOVER ---
    "mimosa": "#MimosaVermillion #BlackClover #GoldenDawn #Mimosa #PlantMagic #MimosaFanart #AIArt",
    "noelle": "#NoelleSilva #BlackClover #Noelle #BlackBulls #WaterMagic #NoelleSilvaFanart #AnimeGirl #AIArt",
    
    # --- FRIEREN ---
    "fern": "#Fern #Frieren #SousouNoFrieren #FrierenBeyondJourneysEnd #Mage #FernFanart #AIArt",
    
    # --- VOCALOID ---
    "miku": "#HatsuneMiku #Vocaloid #Miku #VirtualDiva #MikuHatsune #MikuFanart #AnimeGirl #AIArt",
    
    # --- DARLING IN THE FRANXX ---
    "zerotwo": "#ZeroTwo #DarlingInTheFranxx #DitF #02 #Code002 #ZeroTwoWaifu #ZeroTwoFanart #AIArt",
    
    # --- DRESS UP DARLING ---
    "marin": "#MarinKitagawa #MyDressUpDarling #SonoBisqueDoll #Marin #Cosplayer #MarinKitagawaFanart #AIArt",
    
    # --- SHIELD HERO ---
    "raph": "#Raphtalia #ShieldHero #TateNoYuusha #RaphtaliaWaifu #DemiHuman #RaphtaliaFanart #AIArt"
}

# --- CLEANED FILE MAPPING (Based on your provided file list) ---
# Format: "Keyword": ("DB_Key", "Formal Name", "Series Name")
CHAR_MAP = {
    "a18": ("android18", "Android 18", "Dragon Ball"),
    "akeno": ("akeno", "Akeno Himejima", "High School DxD"),
    "albedo": ("albedo", "Albedo", "Overlord"),
    "alice": ("alice", "Alice Midgar", "Eminence in Shadow"),
    "anis": ("anis", "Anis", "Nikke"),
    "annie": ("annie", "Annie Leonhart", "Attack on Titan"),
    "ayaka": ("ayaka", "Kamisato Ayaka", "Genshin Impact"),
    "boa": ("boa", "Boa Hancock", "One Piece"),
    "bulma": ("bulma", "Bulma", "Dragon Ball"),
    "chichi": ("chichi", "Chi-Chi", "Dragon Ball"),
    "chizuru": ("chizuru", "Chizuru Mizuhara", "Rent-a-Girlfriend"),
    "darkness": ("darkness", "Darkness", "Konosuba"),
    "ellen": ("ellen", "Ellen Joe", "ZZZ"),
    "erza": ("erza", "Erza Scarlet", "Fairy Tail"),
    "fern": ("fern", "Fern", "Frieren"),
    "furina": ("furina", "Furina", "Genshin Impact"),
    "ganyu": ("ganyu", "Ganyu", "Genshin Impact"),
    "haruhime": ("haruhime", "Haruhime", "DanMachi"),
    "hestia": ("hestia", "Hestia", "DanMachi"),
    "hinata": ("hinata", "Hinata Hyuga", "Naruto"),
    "hutao": ("hutao", "Hu Tao", "Genshin Impact"),
    "ino": ("ino", "Ino Yamanaka", "Naruto"),
    "janedoe": ("jane", "Jane Doe", "ZZZ"),
    "keqing": ("keqing", "Keqing", "Genshin Impact"),
    "koneko": ("koneko", "Koneko Toujou", "High School DxD"),
    "krista": ("krista", "Historia Reiss", "Attack on Titan"),
    "kurumi": ("kurumi", "Kurumi Tokisaki", "Date A Live"),
    "kurumii": ("kurumi", "Kurumi Tokisaki", "Date A Live"), # Typo in file list
    "maki": ("maki", "Maki Oze", "Fire Force"),
    "makima": ("makima", "Makima", "Chainsaw Man"),
    "marin": ("marin", "Marin Kitagawa", "My Dress-Up Darling"),
    "mikasa": ("mikasa", "Mikasa Ackerman", "Attack on Titan"),
    "miku": ("miku", "Hatsune Miku", "Vocaloid"),
    "mimosa": ("mimosa", "Mimosa Vermillion", "Black Clover"),
    "mitsuri": ("mitsuri", "Mitsuri Kanroji", "Demon Slayer"),
    "miyabi": ("miyabi", "Hoshimi Miyabi", "ZZZ"),
    "nami": ("nami", "Nami", "One Piece"),
    "narberal": ("narberal", "Narberal Gamma", "Overlord"),
    "nicole": ("nicole", "Nicole Demara", "ZZZ"),
    "notellee": ("noelle", "Noelle Silva", "Black Clover"),
    "orihime": ("orihime", "Orihime Inoue", "Bleach"),
    "raph": ("raph", "Raphtalia", "Shield Hero"),
    "rias": ("rias", "Rias Gremory", "High School DxD"),
    "rukia": ("rukia", "Rukia Kuchiki", "Bleach"),
    "sakura": ("sakura", "Sakura Haruno", "Naruto"),
    "ssakura": ("sakura", "Sakura Haruno", "Naruto"), # Typo in file list
    "shinobu": ("shinobu", "Shinobu Kocho", "Demon Slayer"),
    "tamaki": ("tamaki", "Tamaki Kotatsu", "Fire Force"),
    "tohka": ("tohka", "Tohka Yatogami", "Date A Live"),
    "tsunade": ("tsunade", "Tsunade", "Naruto"),
    "yor": ("yor", "Yor Forger", "Spy x Family"),
    "zerotwo": ("zerotwo", "Zero Two", "Darling in the Franxx"),
    "zhuyuan": ("zhuyuan", "Zhu Yuan", "ZZZ")
}

# --- DESCRIPTION TEMPLATE ---
DESCRIPTION_TEMPLATE = """
**Character:** {formal_name} ({series_name})
**Source:** Generated with Anione.me

✨ **Want to create your own {formal_name} art?**
You can generate unlimited, unrestricted {formal_name} illustrations using our tool.

👇 **Create Here:**
https://www.anione.me/en?ref_code=deviantart

*All characters depicted are over the age of 18.*

---
*Generated by AI. Unrestricted model.*
#AIArt #Anime #Waifu #GenerativeAI #Anione {tags}
"""

def detect_char(filename):
    lower = filename.lower()
    # Sort keys by length descending to fix "Maki" vs "Makima" and "Sakura" vs "SSakura"
    sorted_keys = sorted(CHAR_MAP.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        if key in lower:
            db_entry = CHAR_MAP[key]
            return db_entry[0], db_entry[1], db_entry[2]
            
    return None, filename.split(".")[0].title(), "Anime"

def get_start_date():
    print("\n📅 SCHEDULE SETUP")
    print("Enter the date for the FIRST upload (e.g., Today or Tomorrow).")
    print("Format: YYYY-MM-DD (e.g., 2025-12-15)")
    while True:
        date_input = input("Enter Start Date: ").strip()
        try:
            start_date = datetime.datetime.strptime(date_input, "%Y-%m-%d")
            print(f"✅ Starting Schedule on: {start_date.strftime('%A, %Y-%m-%d')}")
            return start_date
        except ValueError:
            print("❌ Invalid format. Please use YYYY-MM-DD.")

def apply_watermark(image_path, save_path, watermark_img):
    try:
        base_image = Image.open(image_path).convert("RGBA")
        base_w, base_h = base_image.size
        logo_aspect = watermark_img.width / watermark_img.height
        new_logo_w = int(base_w * LOGO_SCALE)
        new_logo_h = int(new_logo_w / logo_aspect)
        resized_logo = watermark_img.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
        if OPACITY < 255:
            r, g, b, alpha = resized_logo.split()
            alpha = alpha.point(lambda p: p * (OPACITY / 255))
            resized_logo = Image.merge("RGBA", (r, g, b, alpha))
        x_pos = PADDING_X
        y_pos = base_h - new_logo_h - PADDING_Y
        transparent_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        transparent_layer.paste(resized_logo, (x_pos, y_pos), mask=resized_logo)
        final = Image.alpha_composite(base_image, transparent_layer)
        final.convert("RGB").save(save_path, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"❌ Error applying watermark: {e}")
        return False

def main():
    print("--- 🏭 DEVIANTART MASTER FACTORY ---")
    
    if not os.path.exists(INPUT_SAFE): os.makedirs(INPUT_SAFE)
    if not os.path.exists(INPUT_MATURE): os.makedirs(INPUT_MATURE)
    if not os.path.exists(ARCHIVE_ROOT): os.makedirs(ARCHIVE_ROOT)

    safe_files = [f for f in os.listdir(INPUT_SAFE) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
    mature_files = [f for f in os.listdir(INPUT_MATURE) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
    
    needed_safe = SAFE_PER_DAY * 7
    needed_mature = MATURE_PER_DAY * 7
    
    print(f"📸 Safe: {len(safe_files)} (Need {needed_safe})")
    print(f"🔞 Mature: {len(mature_files)} (Need {needed_mature})")

    if len(safe_files) < needed_safe or len(mature_files) < needed_mature:
        print("❌ Not enough images!")
        return

    try:
        watermark_source = Image.open(WATERMARK_FILE).convert("RGBA")
    except:
        print("❌ Error: 'watermark.png' missing.")
        return

    start_date = get_start_date()

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H%M%S")
    batch_folder_name = f"Batch_{today_str}_{time_str}"
    batch_path = os.path.join(OUTPUT_ROOT, batch_folder_name)
    os.makedirs(batch_path)

    random.shuffle(safe_files)
    random.shuffle(mature_files)
    selected_safe = safe_files[:needed_safe]
    selected_mature = mature_files[:needed_mature]

    day_paths = []
    day_files = [] 
    
    for i, day in enumerate(DAYS):
        d_path = os.path.join(batch_path, day)
        os.makedirs(d_path)
        day_paths.append(d_path)
        
        current_date = start_date + datetime.timedelta(days=i)
        date_str = current_date.strftime("%A, %Y-%m-%d")
        
        txt_path = os.path.join(d_path, f"{day}_INFO.txt")
        f = open(txt_path, "w", encoding="utf-8")
        f.write(f"=== {day.upper()} UPLOAD GUIDE ({date_str}) ===\n")
        f.write("REMINDER: Check [x] AI Tools | Uncheck [ ] Free Download\n")
        f.write("=" * 60 + "\n\n") 
        day_files.append(f)

    # --- PROCESS SAFE IMAGES ---
    for i, filename in enumerate(selected_safe):
        day_idx = i % 7
        time_slot_idx = i // 7
        target_dir = day_paths[day_idx]
        current_file = day_files[day_idx]
        
        time_str = SAFE_TIMES[time_slot_idx] if time_slot_idx < len(SAFE_TIMES) else "ASAP"
        
        db_key, formal_name, series_name = detect_char(filename)
        
        emoji_suffix = random.choice(EMOJI_IDS)
        new_name = f"{formal_name} ({series_name}) - Unrestricted AI {emoji_suffix}.jpg"
        
        src = os.path.join(INPUT_SAFE, filename)
        dst = os.path.join(target_dir, new_name)
        
        if apply_watermark(src, dst, watermark_source):
            shutil.move(src, os.path.join(ARCHIVE_ROOT, filename))
            
            tags = TAG_DB.get(db_key, "#AIArt #Anime #Waifu")
            desc = DESCRIPTION_TEMPLATE.format(formal_name=formal_name, series_name=series_name, tags=tags)
            
            current_file.write(f"⏰ SCHEDULE TIME: {time_str} (SAFE)\n")
            current_file.write(f"📁 FILE: {new_name}\n")
            current_file.write(f"⚙️ SETTINGS: [x] AI Tools | [ ] Free Download | [ ] Mature\n\n")
            current_file.write(f"🏷️ TAGS:\n{tags}\n\n")
            current_file.write(f"📝 DESCRIPTION:\n{desc}\n")
            current_file.write("\n" + "="*60 + "\n\n")

    # --- PROCESS MATURE IMAGES ---
    for i, filename in enumerate(selected_mature):
        day_idx = i % 7
        time_slot_idx = i // 7
        target_dir = day_paths[day_idx]
        current_file = day_files[day_idx]

        time_str = MATURE_TIMES[time_slot_idx] if time_slot_idx < len(MATURE_TIMES) else "ASAP"

        db_key, formal_name, series_name = detect_char(filename)
        
        emoji_suffix = random.choice(EMOJI_IDS)
        new_name = f"[NSFW] {formal_name} ({series_name}) - Unrestricted AI {emoji_suffix}.jpg"
        
        src = os.path.join(INPUT_MATURE, filename)
        dst = os.path.join(target_dir, new_name)
        
        if apply_watermark(src, dst, watermark_source):
            shutil.move(src, os.path.join(ARCHIVE_ROOT, filename))
            
            tags = TAG_DB.get(db_key, "#AIArt #Anime #NSFW")
            desc = DESCRIPTION_TEMPLATE.format(formal_name=formal_name, series_name=series_name, tags=tags)
            
            current_file.write(f"⏰ SCHEDULE TIME: {time_str} (MATURE)\n")
            current_file.write(f"📁 FILE: {new_name}\n")
            current_file.write(f"⚙️ SETTINGS: [x] AI Tools | [ ] Free Download | [x] Mature (CHECK THIS!)\n\n")
            current_file.write(f"🏷️ TAGS:\n{tags}\n\n")
            current_file.write(f"📝 DESCRIPTION:\n{desc}\n")
            current_file.write("\n" + "="*60 + "\n\n")

    for f in day_files:
        f.close()

    print(f"✨ DONE! Batch created: {batch_folder_name}")
    print(f"📄 Helper files created inside each Day Folder.")
    print("📁 Used images moved to '4_Archived'")

if __name__ == "__main__":
    main()