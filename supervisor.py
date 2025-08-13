
import time
from apscheduler.schedulers.background import BackgroundScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import utils
from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, SUMMARY_EMAIL_TO

def monitor_and_consolidate():
    print("Supervisor: Monitoring sheet...")
    sheet = utils.get_sheet()
    data = sheet.get_all_values()
    if len(data) < 2:
        print("Supervisor: No leads in sheet.")
        return  # No leads

    # Count stats
    total_leads = len(data) - 1  # Exclude header
    verified = sum(1 for row in data[1:] if row[5] == 'Y')
    interested = sum(1 for row in data[1:] if row[6] == 'Interested')
    not_interested = sum(1 for row in data[1:] if row[6] == 'Not Interested')
    no_response = sum(1 for row in data[1:] if row[6] in ['No Response', 'Sent/No Response'])
    # Only consider leads with Email Verified = 'Y' as pending if Response Status is empty
    pending = any(row[5] == 'Y' and row[6] == '' for row in data[1:])

    # Log current state
    print(f"Total Leads: {total_leads}, Verified: {verified}, Interested: {interested}, Not Interested: {not_interested}, No Response: {no_response}, Pending: {pending}")

    # Send summary if no pending leads
    if not pending:
        summary = f"Campaign Summary:\nTotal Leads: {total_leads}\nVerified: {verified}\nInterested: {interested}\nNot Interested: {not_interested}\nNo Response: {no_response}"
        print(summary)
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=SUMMARY_EMAIL_TO,
            subject='Sales Campaign Summary',
            plain_text_content=summary)
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"Summary email sent: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error sending summary: {e}")

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_and_consolidate, 'interval', minutes=3)  # Check every 3 min
    scheduler.start()
    print("Supervisor started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()