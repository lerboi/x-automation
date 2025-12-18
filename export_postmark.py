import requests
import csv
import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from disposable_email_domains import blocklist

# ================= CONFIGURATION =================
load_dotenv()
SERVER_TOKEN = os.getenv("POSTMARK_SERVER_TOKEN")

if not SERVER_TOKEN:
    print("❌ Error: 'POSTMARK_SERVER_TOKEN' not found in .env file.")
    sys.exit(1)

DAYS_TO_LOOK_BACK = 45 
VALID_STATUSES = {'queued', 'sent', 'delivered', 'opened'}

# Disposable domains setup
custom_bad_domains = {"uorak.com", "laoia.com", "wivstore.com", "nespf.com", "comfythings.com"}
all_bad_domains = set(blocklist).union(custom_bad_domains)
# =================================================

def get_user_input():
    print("\n--- Postmark Smart Exporter (Resumable) ---")
    print(f"Available statuses: {', '.join(sorted(VALID_STATUSES))}")
    print("Tip: You can enter multiple separated by commas (e.g. 'opened, delivered')")
    
    while True:
        raw_input = input("Enter statuses to fetch: ").strip().lower()
        selected_statuses = [s.strip() for s in raw_input.split(',') if s.strip()]
        invalid_inputs = [s for s in selected_statuses if s not in VALID_STATUSES]
        
        if invalid_inputs:
            print(f"⚠️ Invalid status: {', '.join(invalid_inputs)}")
        elif not selected_statuses:
            print("⚠️ Input cannot be empty.")
        else:
            return selected_statuses

def get_checkpoint(status):
    """Reads the checkpoint file to find the last date index we completed."""
    filename = f"checkpoint_{status}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f).get("last_day_index", -1)
    return -1

def save_checkpoint(status, day_index):
    """Saves the current progress so we can resume later."""
    filename = f"checkpoint_{status}.json"
    with open(filename, 'w') as f:
        json.dump({"last_day_index": day_index}, f)

def fetch_emails(status_filter):
    print(f"\n🚀 Starting Export for Status: {status_filter.upper()}")
    
    # 1. Load existing emails to prevent duplicates if resuming
    csv_filename = f"postmark_{status_filter}_users.csv"
    unique_emails = set()
    
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Email"):
                    unique_emails.add(row["Email"])
        print(f"   🔄 Resuming: Loaded {len(unique_emails)} existing emails from CSV.")
    else:
        # Initialize CSV with header
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Email"])
            writer.writeheader()

    # 2. Determine start day
    start_day_index = get_checkpoint(status_filter) + 1
    
    if start_day_index >= DAYS_TO_LOOK_BACK:
        print(f"   ✅ This status is already fully exported up to {DAYS_TO_LOOK_BACK} days ago.")
        return

    headers = {
        "X-Postmark-Server-Token": SERVER_TOKEN,
        "Accept": "application/json"
    }

    skipped_count = 0
    
    # 3. Loop Day-by-Day (The only way to get >10k records)
    for i in range(start_day_index, DAYS_TO_LOOK_BACK):
        # Time logic: We go backwards. Day 0 = Today, Day 1 = Yesterday...
        date_target = datetime.now() - timedelta(days=i)
        date_next = date_target + timedelta(days=1)
        
        from_date_str = date_target.strftime('%Y-%m-%d')
        to_date_str = date_next.strftime('%Y-%m-%d')
        
        offset = 0
        count_per_req = 500
        keep_fetching_day = True
        
        print(f"   Processing Date: {from_date_str}...", end='\r')
        
        day_emails = [] # Store emails for this specific day to write in batch

        while keep_fetching_day:
            # We use /messages/outbound for EVERYTHING now. It supports filtering by status='opened'
            # This bypasses the 10k limit of the /opens endpoint.
            url = "https://api.postmarkapp.com/messages/outbound"
            params = {
                "count": count_per_req,
                "offset": offset,
                "status": status_filter,
                "fromDate": from_date_str,
                "toDate": to_date_str
            }

            try:
                response = requests.get(url, headers=headers, params=params)
                
                # If we hit the hard 10k limit for a SINGLE DAY, we must skip to next day
                if response.status_code == 422:
                    keep_fetching_day = False
                    continue 

                if response.status_code != 200:
                    print(f"\n❌ API Error: {response.status_code} - {response.text}")
                    return

                data = response.json()
                messages = data.get("Messages", [])

                if not messages:
                    keep_fetching_day = False
                    continue

                for msg in messages:
                    recipient = msg.get("To", [{}])[0].get("Email")
                    
                    if recipient:
                        # --- DISPOSABLE CHECK ---
                        try:
                            domain = recipient.split('@')[-1].lower().strip()
                            if domain in all_bad_domains:
                                skipped_count += 1
                                continue
                        except:
                            continue
                        # ------------------------

                        if recipient not in unique_emails:
                            unique_emails.add(recipient)
                            day_emails.append({"Email": recipient})

                offset += count_per_req
                if offset >= data.get("TotalCount", 0):
                    keep_fetching_day = False
            
            except Exception as e:
                print(f"\n❌ Error: {e}")
                return # Stop script on network error so we don't save a bad state

        # 4. Save Batch to CSV (Append Mode)
        if day_emails:
            with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["Email"])
                writer.writerows(day_emails)
        
        # 5. Save Checkpoint
        save_checkpoint(status_filter, i)

    print(f"\n✅ Finished {status_filter.upper()}. Total Unique: {len(unique_emails)} | Blocked Junk: {skipped_count}")
    # Optional: Delete checkpoint when fully done
    # os.remove(f"checkpoint_{status_filter}.json")

if __name__ == "__main__":
    try:
        statuses_to_run = get_user_input()
        for status in statuses_to_run:
            fetch_emails(status)
        print("\n🎉 All tasks completed.")
    except KeyboardInterrupt:
        print("\n\nOperation paused by user. Progress saved.")
        sys.exit(0)