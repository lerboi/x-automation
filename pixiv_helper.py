import os
import random
import shutil
import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.join(BASE_DIR, "pixiv_batches")
POSTING_DIR = os.path.join(INPUT_ROOT, ".POSTING")
OUTPUT_FILE = os.path.join(BASE_DIR, "pixiv_upload_guide.txt")

# --- THE MASTER TAG DATABASE (45 Characters | JP + EN) ---
TAG_DB = {
    # --- A ---
    "aiz": "#AizWallenstein #アイズ・ヴァレンシュタイン #DanMachi #ダンまち #SwordOratoria #ソード・オラトリア #AIイラスト",
    "akeno": "#AkenoHimejima #姫島朱乃 #HighSchoolDxD #ハイスクールD×D #RiasGremory #リアス・グレモリー #AIイラスト",
    "alexia": "#AlexiaMidgar #アレクシア・ミドガル #TheEminenceInShadow #陰の実力者になりたくて! #阴の実力者になりたくて! #AIイラスト",
    "alya": "#Alya #アーリャ #Roshidere #ロシデレ #AlisaMikhailovnaKujou #アリサ・ミハイロヴナ・九条 #AIイラスト",
    "android": "#Android18 #人造人間18号 #DragonBall #ドラゴンボール #C18 #Lazuli #AIイラスト",
    "annie": "#AnnieLeonhart #アニ・レオンハート #AttackOnTitan #進撃の巨人 #FemaleTitan #女型の巨人 #AIイラスト",
    
    # --- B ---
    "boa": "#BoaHancock #ボア・ハンコック #OnePiece #ワンピース #PirateEmpress #海賊女帝 #AIイラスト",
    "bocchi": "#HitoriGotoh #後藤ひとり #BocchiTheRock #ぼっち・ざ・ろっく! #BTR #結束バンド #AIイラスト",
    "bulma": "#Bulma #ブルマ #DragonBall #ドラゴンボール #BulmaBriefs #AIイラスト",
    
    # --- C ---
    "chichi": "#ChiChi #チチ #DragonBall #ドラゴンボール #Milk #AIイラスト",
    
    # --- D ---
    "darkness": "#Darkness #ダクネス #Konosuba #このすば #Lalatina #ララティーナ #AIイラスト",
    
    # --- E ---
    "erza": "#ErzaScarlet #エルザ・スカーレット #FairyTail #フェアリーテイル #Titania #妖精女王 #AIイラスト",
    
    # --- F ---
    "fern": "#Fern #フェルン #Frieren #葬送のフリーレン #SousouNoFrieren #AIイラスト",
    "furina": "#Furina #フリーナ #GenshinImpact #原神 #Focalors #フォカロルス #AIイラスト",
    
    # --- H ---
    "haruhime": "#SanjounoHaruhime #サンジョウノ・春姫 #DanMachi #ダンまち #Renard #ルナール #AIイラスト",
    "hestia": "#Hestia #ヘスティア #DanMachi #ダンまち #LoliKami #例の紐 #AIイラスト",
    "hinata": "#HinataHyuga #日向ヒナタ #Naruto #ナルト #Byakugan #白眼 #AIイラスト",
    
    # --- K ---
    "koneko": "#KonekoToujou #塔城小猫 #HighSchoolDxD #ハイスクールD×D #Nekomata #猫又 #AIイラスト",
    "krista": "#HistoriaReiss #ヒストリア・レイス #KristaLenz #クリスタ・レンズ #AttackOnTitan #進撃の巨人 #AIイラスト",
    "kurumi": "#KurumiTokisaki #時崎狂三 #DateALive #デート・ア・ライブ #Nightmare #ナイトメア #AIイラスト",
    
    # --- M ---
    "maki": "#MakiOze #茉希尾瀬 #FireForce #炎炎ノ消防隊 #Witch #ゴリラサイクロプス #AIイラスト",
    "makima": "#Makima #マキマ #ChainsawMan #チェンソーマン #ControlDevil #支配の悪魔 #AIイラスト",
    "marin": "#MarinKitagawa #喜多川海夢 #SonoBisqueDoll #着せ恋 #MyDressUpDarling #その着せ替え人形は恋をする #AIイラスト",
    "mikasa": "#MikasaAckerman #ミカサ・アッカーマン #AttackOnTitan #進撃の巨人 #Mikasa #ミカサ #AIイラスト",
    "miku": "#HatsuneMiku #初音ミク #Vocaloid #ボーカロイド #Miku #ミク #AIイラスト",
    "mimosa": "#MimosaVermillion #ミモザ・ヴァーミリオン #BlackClover #ブラッククローバー #GoldenDawn #金色の夜明け #AIイラスト",
    "mirajane": "#MirajaneStrauss #ミラジェーン・ストラウス #FairyTail #フェアリーテイル #SheDevil #魔人 #AIイラスト",
    "misty": "#Misty #カスミ #Pokemon #ポケモン #PokeGirl #ポケ女 #AIイラスト",
    "mitsuri": "#MitsuriKanroji #甘露寺蜜璃 #DemonSlayer #鬼滅の刃 #KimetsuNoYaiba #恋柱 #AIイラスト",
    
    # --- N ---
    "nami": "#Nami #ナミ #OnePiece #ワンピース #CatBurglar #泥棒猫 #AIイラスト",
    "nicole": "#NicoleDemara #ニコ・デマラ #ZenlessZoneZero #ゼンレスゾーンゼロ #ZZZ #CunningHares #AIイラスト",
    "noelle": "#NoelleSilva #ノエル・シルヴァ #BlackClover #ブラッククローバー #BlackBulls #黒の暴牛 #AIイラスト",
    
    # --- O ---
    "orihime": "#OrihimeInoue #井上織姫 #Bleach #ブリーチ #KurosakiOrihime #黒崎織姫 #AIイラスト",
    
    # --- R ---
    "raphtalia": "#Raphtalia #ラフタリア #ShieldHero #盾の勇者の成り上がり #TateNoYuusha #亜人 #AIイラスト",
    "rias": "#RiasGremory #リアス・グレモリー #HighSchoolDxD #ハイスクールD×D #CrimsonHairedRuinPrincess #紅髪の滅殺姫 #AIイラスト",
    "rukia": "#RukiaKuchiki #朽木ルキア #Bleach #ブリーチ #Shinigami #死神 #AIイラスト",
    
    # --- S ---
    "sakura": "#SakuraHaruno #春野サクラ #Naruto #ナルト #UchihaSakura #うちはサクラ #AIイラスト",
    "sasha": "#SashaBraus #サシャ・ブラウス #AttackOnTitan #進撃の巨人 #PotatoGirl #芋女 #AIイラスト",
    "secre": "#SecreSwallowtail #セクレ・スワロテイル #Nero #ネロ #BlackClover #ブラッククローバー #AIイラスト",
    "shinobu": "#ShinobuKocho #胡蝶しのぶ #DemonSlayer #鬼滅の刃 #KimetsuNoYaiba #蟲柱 #AIイラスト",
    "suzune": "#SuzuneHorikita #堀北鈴音 #ClassroomOfTheElite #よう実 #YouZitsu #ようこそ実力至上主義の教室へ #AIイラスト",
    
    # --- T ---
    "tamaki": "#TamakiKotatsu #環古達 #FireForce #炎炎ノ消防隊 #LuckyLecherLure #ラッキースケベられ #AIイラスト",
    "tohka": "#TohkaYatogami #夜刀神十香 #DateALive #デート・ア・ライブ #Princess #プリンセス #AIイラスト",
    "tsunade": "#Tsunade #綱手 #Naruto #ナルト #Hokage #五代目火影 #AIイラスト",
    
    # --- Y ---
    "yor": "#YorForger #ヨル・フォージャー #SpyxFamily #スパイファミリー #ThornPrincess #いばら姫 #AIイラスト",
    
    # --- Z ---
    "zerotwo": "#ZeroTwo #ゼロツー #DarlingInTheFranxx #ダリフラ #Code002 #コード002 #AIイラスト",
}

# --- NEW CLICKY TITLES (Hearts + 18 Only + Unrestricted) ---
PIXIV_TITLES = [
    "【Unrestricted】 {char} 🔞",
    "{char} ❤️ (Unrestricted)",
    "【AI】 {char} 🔞💖",
    "{char} | Unrestricted 💘",
    "【High Quality】 {char} 🔞",
    "{char} (Anione AI) 💓"
]

# --- HIGH INTENT TEMPLATE ---
DESCRIPTION_TEMPLATE = """【 {char_name} | Anione.me で生成 】

🔞 制限なしのAI画像生成。あなただけの理想のキャラを作ろう！
👇 作成はこちら:
https://www.anione.me/jp?ref_code=pixiv

🔥 クーポンコード「PIXIV」で15%OFF！

---
✨ Want to create your own {char_name} art?
Generate Unrestricted AI Anime Art here:
👇 Create now:
https://www.anione.me/en?ref_code=pixiv

🔥 Use code "PIXIV" for 15% OFF!
#AI #AIart #AIイラスト #Anione"""

# --- SCHEDULING LOGIC ---
BEST_TIME_JST = "20:00 JST" # The universal "Golden Hour" for Japan/Global mix

def get_char_key(folder_name):
    """Fuzzy match folder name to DB key."""
    normalized = folder_name.lower().replace(" ", "")
    sorted_keys = sorted(TAG_DB.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        if normalized.startswith(key):
            return key
    return None

def get_start_date():
    """Asks user for a specific date and returns a datetime object."""
    print("\n📅 WEEKLY SCHEDULE SETUP")
    print("Please enter the date for the FIRST upload.")
    print("Format: YYYY-MM-DD (e.g., 2025-12-15)")
    
    while True:
        date_input = input("Enter Date: ").strip()
        try:
            # Parse date
            start_date = datetime.datetime.strptime(date_input, "%Y-%m-%d")
            # Confirm with user
            day_name = start_date.strftime("%A")
            print(f"✅ Selected: {day_name}, {date_input}")
            return start_date
        except ValueError:
            print("❌ Invalid format. Please use YYYY-MM-DD (Year-Month-Day).")

def draft_weekly_batch():
    # 1. Setup Folders
    if not os.path.exists(INPUT_ROOT):
        os.makedirs(INPUT_ROOT)
        print("⚠️ 'pixiv_batches' folder created. Put your folders there first!")
        return
    if not os.path.exists(POSTING_DIR):
        os.makedirs(POSTING_DIR)

    # 2. Get Start Date
    start_date = get_start_date()
    
    # 3. Scan available folders
    all_items = os.listdir(INPUT_ROOT)
    available_folders = []
    
    print(f"\n🔍 Scanning '{INPUT_ROOT}'...")
    for item in all_items:
        path = os.path.join(INPUT_ROOT, item)
        if os.path.isdir(path) and item != ".POSTING":
            available_folders.append(item)

    if not available_folders:
        print("❌ No folders found. (Did you put them inside 'pixiv_batches'?)")
        return

    # 4. Group by Character
    char_map = {} 
    valid_count = 0
    
    for folder in available_folders:
        key = get_char_key(folder)
        if key:
            if key not in char_map: char_map[key] = []
            char_map[key].append(folder)
            valid_count += 1
            print(f"   ✅ Matched: '{folder}' -> Key: '{key}'")
        else:
            print(f"   ⚠️  Unknown Character: '{folder}'")

    print(f"📊 Found {valid_count} valid folders.\n")

    # 5. Select 7 Folders (Diverse Selection)
    selected_folders = []
    unique_chars = list(char_map.keys())
    random.shuffle(unique_chars)

    while len(selected_folders) < 7 and unique_chars:
        char = unique_chars.pop(0) 
        folder = char_map[char].pop(0) 
        selected_folders.append(folder)
        if not char_map[char]:
            pass 

    remaining_folders = []
    for folders in char_map.values():
        remaining_folders.extend(folders)
    random.shuffle(remaining_folders)
    
    while len(selected_folders) < 7 and remaining_folders:
        selected_folders.append(remaining_folders.pop(0))

    if not selected_folders:
        print("❌ Not enough valid character folders found.")
        return

    print(f"✅ Selected {len(selected_folders)} folders for this week.")

    # 6. Move to .POSTING and Generate Guide
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== 📅 WEEKLY PIXIV BATCH GUIDE ===\n")
        f.write("Instructions: Folders have been moved to '.POSTING'.\n")
        f.write("Upload 1 folder per day at the scheduled time.\n\n")

        for i, folder_name in enumerate(selected_folders):
            # Calculate Schedule
            current_date = start_date + datetime.timedelta(days=i)
            day_name = current_date.strftime("%A")
            date_str = current_date.strftime("%Y-%m-%d")
            
            src = os.path.join(INPUT_ROOT, folder_name)
            dst = os.path.join(POSTING_DIR, folder_name)
            shutil.move(src, dst)
            
            key = get_char_key(folder_name)
            tags = TAG_DB.get(key, "#AIart")
            tags += " #Anione" 
            
            char_title = key.title() if key else folder_name
            title_template = random.choice(PIXIV_TITLES)
            final_title = title_template.format(char=char_title)
            
            f.write("="*20 + f" DAY {i+1}: {day_name.upper()} ({date_str}) " + "="*20 + "\n")
            f.write(f"⏰ SCHEDULE: {date_str} @ {BEST_TIME_JST}\n")
            f.write(f"📂 FOLDER: {folder_name}\n")
            f.write("-" * 40 + "\n")
            f.write(f"[TITLE]\n{final_title}\n\n")
            f.write(f"[TAGS]\n{tags}\n\n")
            f.write(f"[DESCRIPTION]\n{DESCRIPTION_TEMPLATE.format(char_name=char_title)}\n")
            f.write("\n\n")

    print(f"🚀 SUCCESS! Moved 7 folders to '{POSTING_DIR}'.")
    print(f"📄 Upload Guide generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    draft_weekly_batch()