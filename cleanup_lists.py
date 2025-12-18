import csv
import os
import sys

def clean_lists():
    print("--- Email List Deduplicator ---")
    
    # 1. Get File Names
    file_a = input("Enter the filename for List A (VIP/Opened): ").strip()
    file_b = input("Enter the filename for List B (Sent/Cold): ").strip()

    # Basic Validation
    if not os.path.exists(file_a) or not os.path.exists(file_b):
        print("❌ Error: One or both files could not be found. Check the names.")
        return

    # 2. Load List A (VIPs) into a Set for fast lookup
    vip_emails = set()
    print(f"\n📖 Reading {file_a}...")
    
    try:
        with open(file_a, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Auto-detect the email column name if it varies
            email_col = next((col for col in reader.fieldnames if 'email' in col.lower()), 'Email')
            
            for row in reader:
                if row[email_col]:
                    # Normalize: lowercase and strip spaces
                    vip_emails.add(row[email_col].strip().lower())
                    
        print(f"✅ Loaded {len(vip_emails)} VIP emails.")

    except Exception as e:
        print(f"❌ Error reading List A: {e}")
        return

    # 3. Process List B and Remove VIPs
    cleaned_records = []
    removed_count = 0
    total_b_count = 0
    
    print(f"🧹 Scrubbing {file_b}...")
    
    try:
        with open(file_b, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Auto-detect email column for file B as well
            email_col_b = next((col for col in reader.fieldnames if 'email' in col.lower()), 'Email')
            
            for row in reader:
                total_b_count += 1
                email = row[email_col_b].strip().lower()
                
                if email in vip_emails:
                    removed_count += 1
                else:
                    cleaned_records.append(row)

    except Exception as e:
        print(f"❌ Error reading List B: {e}")
        return

    # 4. Save the Result
    output_filename = "cleaned_cold_list.csv"
    
    try:
        with open(output_filename, mode='w', newline='', encoding='utf-8') as f:
            # Use fieldnames from the original file B to keep structure
            writer = csv.DictWriter(f, fieldnames=cleaned_records[0].keys())
            writer.writeheader()
            writer.writerows(cleaned_records)
            
        print("\n" + "="*30)
        print(f"🎉 DONE! Cleanup Complete.")
        print(f"------------------------------")
        print(f"📂 Original Cold List Size: {total_b_count}")
        print(f"🚫 VIPs Removed:            {removed_count}")
        print(f"✅ Final Clean List Size:   {len(cleaned_records)}")
        print(f"------------------------------")
        print(f"💾 Saved as: {output_filename}")
        print("="*30)

    except IndexError:
        print("⚠️ Warning: The result list was empty. No file saved.")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    clean_lists()