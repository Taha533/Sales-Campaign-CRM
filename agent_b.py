

import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import utils
from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, BASE_URL
from datetime import datetime, timedelta
import re

def perform_outreach():
    print("Agent B: Performing outreach...")
    sheet = utils.get_sheet()
    data = sheet.get_all_values()
    updated = False
    for i, row in enumerate(data[1:], start=2):
        if row[5] == 'Y' and row[6] == '' and row[1]:  # Verified, no response status, email exists
            email = row[1]
            lead_name = row[0] or "Lead"  # Fallback if name is empty
            # Generate unique tracking links
            interested_url = f"{BASE_URL}/respond?lead_id={i}&response=interested"
            not_interested_url = f"{BASE_URL}/respond?lead_id={i}&response=not_interested"
            # Send campaign email
            message = Mail(
                from_email=SENDGRID_FROM_EMAIL,
                to_emails=email,
                subject='Exciting Sales Opportunity!',
                plain_text_content=f"""Dear {lead_name},

We're reaching out with a great offer for your company in the {row[4] or 'your'} industry.

Please click one of the following:
- Yes, I'm Interested: {interested_url}
- No, not Interested: {not_interested_url}

Best,
Sales Team""")
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                response = sg.send(message)
                status = 'Sent/No Response' if response.status_code == 202 else 'Failed'
                notes = f"HTTP {response.status_code}, Sent at {datetime.utcnow().isoformat()}"
                # Update sheet
                sheet.update_cell(i, 7, status)  # Column G (7)
                sheet.update_cell(i, 8, notes)   # Column H (8)
                print(f"Outreach to {email}: {status}")
                updated = True
            except Exception as e:
                status = 'Failed'
                notes = str(e)
                sheet.update_cell(i, 7, status)
                sheet.update_cell(i, 8, notes)
                print(f"Error sending to {email}: {e}")
    if not updated:
        print("Agent B: No new verified leads to contact.")

def check_timeouts():
    print("Agent B: Checking for response timeouts...")
    sheet = utils.get_sheet()
    data = sheet.get_all_values()
    updated = False
    current_time = datetime.utcnow()
    for i, row in enumerate(data[1:], start=2):
        if row[6] == 'Sent/No Response' and row[1]:
            # Extract sent timestamp from Notes (e.g., "HTTP 202, Sent at 2025-08-13T...")
            notes = row[7]
            match = re.search(r'Sent at ([\d-]+T[\d:]+)', notes)
            if match:
                sent_time = datetime.fromisoformat(match.group(1))
                if current_time - sent_time > timedelta(days=7):
                    sheet.update_cell(i, 7, 'No Response')  # Column G (7)
                    sheet.update_cell(i, 8, f"Timed out at {current_time.isoformat()}")  # Column H (8)
                    print(f"Updated {row[1]} to No Response (timeout)")
                    updated = True
    if not updated:
        print("Agent B: No leads timed out.")

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(perform_outreach, 'interval', minutes=2)  # Outreach every 2 min
    scheduler.add_job(check_timeouts, 'interval', minutes=60)   # Check timeouts every hour
    scheduler.start()
    print("Agent B started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()