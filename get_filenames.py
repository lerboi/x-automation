import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# It scans both folders we set up
FOLDERS_TO_SCAN = [
    os.path.join(BASE_DIR, "deviantart_workflow", "1_Raw_Safe"),
    os.path.join(BASE_DIR, "deviantart_workflow", "1_Raw_Mature")
]
OUTPUT_FILE = os.path.join(BASE_DIR, "all_filenames.txt")

def scan_files():
    found_files = []
    
    print("🔍 Scanning folders...")
    for folder in FOLDERS_TO_SCAN:
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            found_files.extend(files)
            print(f"   ✅ Found {len(files)} images in: {os.path.basename(folder)}")
        else:
            print(f"   ⚠️ Folder not found: {folder}")

    # Sort alphabetically to make it easy to read
    found_files.sort()

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(found_files))

    print("-" * 30)
    print(f"📄 Successfully saved {len(found_files)} filenames to: {OUTPUT_FILE}")
    print("👉 Please open that text file and paste the list back to the AI.")

if __name__ == "__main__":
    scan_files()