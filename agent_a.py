


import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import utils
from config import HUNTER_API_KEY

def verify_leads():
    print("Agent A: Verifying leads...")
    sheet = utils.get_sheet()
    data = sheet.get_all_values()
    updated = False
    for i, row in enumerate(data[1:], start=2):  # Start from row 2
        if row[5] == '' and row[1]:  # Check if Email Verified is empty and email exists
            email = row[1]
            # Verify email using Hunter.io API
            url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    result = response.json()['data']
                    verified = 'Y' if result['result'] == 'deliverable' else 'N'
                    notes = result.get('reason', '')
                else:
                    verified = 'N'
                    notes = f"API error: HTTP {response.status_code}"
                # Update sheet
                sheet.update_cell(i, 6, verified)  # Column F (6)
                sheet.update_cell(i, 8, notes)     # Column H (8)
                print(f"Verified {email}: {verified}")
                updated = True
            except Exception as e:
                print(f"Error verifying {email}: {e}")
    if not updated:
        print("Agent A: No new leads to verify.")

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(verify_leads, 'interval', minutes=1)  # Check every 1 min
    scheduler.start()
    print("Agent A started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()