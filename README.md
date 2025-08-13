# Sales Campaign CRM

This project implements a Sales Campaign Customer Relationship Management (CRM) system as part of the GEN AI Engineer role interview task at Petabytz Technologies. The system automates lead processing, email verification, outreach, and response tracking using a Google Sheet as the data store. It consists of three agents (Supervisor, Agent A, Agent B) and a FastAPI server for handling response tracking via links.

## Use Case

The system processes leads from a Google Sheet, verifies email addresses, sends outreach emails with tracking links, captures responses ("Interested," "Not Interested," "No Response"), and generates a summary report via email.

### Components

- **Supervisor Agent**: Monitors the Google Sheet, consolidates results, and sends a summary email when all verified leads are processed.
- **Agent A**: Verifies lead email addresses using the Hunter.io API and updates the sheet.
- **Agent B**: Sends outreach emails via SendGrid with "Interested" and "Not Interested" tracking links, updates statuses based on link clicks, and marks leads as "No Response" after a 7-day timeout.
- **FastAPI Server**: Handles link clicks to update response statuses in the Google Sheet.

## Prerequisites

- **Python 3.10+** with a virtual environment (e.g., `sales_campaign`).
- **Google Cloud Project**:
  - Enable Google Sheets API.
  - Create a service account and download `credentials.json`.
  - Share the Google Sheet with the service account email (found in `credentials.json` under `client_email`).
  - Here, credential.json is "sales-campaign-468803-cf92243fa547.json"
- **Google Sheet**:
  - Create a sheet named "Sales Leads" with columns: `Lead Name`, `Email`, `Contact Number`, `Company`, `Industry`, `Email Verified (Y/N)`, `Response Status`, `Notes`.
  - Note the Sheet ID from the URL (`https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`).
- **API Keys**:
  - **Hunter.io**: Sign up at hunter.io for an API key (free tier: 50 verifications/month).
  - **SendGrid**: Sign up at sendgrid.com, get an API key, and verify a sender email.

## Installation

1. **Clone the Repository** (or create project directory):

   ```bash
   mkdir sales_campaign_crm
   cd sales_campaign_crm
   ```
2. **Set Up Virtual Environment**:

   ```bash
   conda create -n sales_campaign python=3.10
   ```
3. **Install Dependencies**:

   ```bash
   pip install gspread oauth2client apscheduler requests sendgrid python-dotenv fastapi uvicorn
   ```
4. **Configure Environment Variables**:
   - Create a `.env` file in the project directory:

     ```
     GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
     SHEET_ID=your_google_sheet_id
     HUNTER_API_KEY=your_hunter_api_key
     SENDGRID_API_KEY=your_sendgrid_api_key
     SENDGRID_FROM_EMAIL=your_verified_sender@yourdomain.com
     SUMMARY_EMAIL_TO=manager@company.com
     BASE_URL=http://localhost:8000 
     ```
   - Place `credentials.json` in the specified path.

## Project Structure

```
sales_campaign/
├── sales-campaign-468803-cf92243fa547.json      # Google Cloud service account credentials
├── .env                   # Environment variables
├── config.py              # Configuration loading
├── utils.py               # Google Sheets utility
├── supervisor.py          # Supervisor Agent script
├── agent_a.py             # Agent A (email verification) script
├── agent_b.py             # Agent B (outreach and response tracking) script
├── server.py              # FastAPI server for response tracking
├── README.md              # This file
├── environment.yml
```

## Setup

1. **Google Sheet**:
   - Create a Google Sheet with headers: `Lead Name`, `Email`, `Contact Number`, `Company`, `Industry`, `Email Verified (Y/N)`, `Response Status`, `Notes`.
   - Share with the service account email (from `credentials.json`).
2. **FastAPI Server**:

- For local testing, use `http://localhost:8000` in `.env`.

## Running the System

1. **Start FastAPI Server**:

   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```
2. **Run Agents** (in separate terminals):

   ```bash
   python supervisor.py
   python agent_a.py
   python agent_b.py
   ```
3. **Add Test Leads**:
   - In the Google Sheet, add rows like:

     ```
     Lead Name | Email                      | Contact Number | Company       | Industry | Email Verified | Response Status | Notes
     John Doe  | john@example.com          | 123-456-7890   | Example Corp  | Tech     |                |                 | 
     Test Lead | muhammadtaha7579@gmail.com| 23-456-7890    | Test Corp     | Tech     |                |                 | 
     Test Lead 3 | anotheremail@gmail.com  | 555-555-5555   | Another Corp  | Finance   |                |                 | 
     ```

## How It Works

1. **Agent A (Email Verification)**:
   - Runs every 1 minute.
   - Uses Hunter.io API to verify emails in the "Email" column.
   - Updates "Email Verified" (Y/N) and "Notes" (e.g., API errors or reason).
2. **Agent B (Outreach and Response Tracking)**:
   - **Outreach**: Runs every 2 minutes, sends emails to verified leads ("Email Verified" = "Y") via SendGrid, including links:
     - `Yes, I'm Interested: {BASE_URL}/respond?lead_id={row}&response=interested`
     - `No, not Interested: {BASE_URL}/respond?lead_id={row}&response=not_interested`
     - Sets "Response Status" to "Sent/No Response" and "Notes" with timestamp.
   - **Timeout**: Runs every 60 minutes, marks leads as "No Response" if no link clicked after 7 days.
3. **FastAPI Server**:
   - Handles `/respond` endpoint to update "Response Status" ("Interested" or "Not Interested") when links are clicked.
4. **Supervisor Agent**:
   - Runs every 3 minutes.
   - Counts verified, interested, not interested, and no-response leads.
   - Sends a summary email to `SUMMARY_EMAIL_TO` when all verified leads have a response status.

## Testing

1. **End-to-End Test**:

- Add test leads to the Google Sheet.
- Wait 1–2 minutes:
  - Agent A verifies emails (e.g., `john@example.com` → "N", others → "Y").
  - Agent B sends emails to verified leads with tracking links.
- Click links in received emails:
  - Check Google Sheet: "Response Status" updates to "Interested" or "Not Interested".

- Wait 3 minutes for Supervisor to send summary email to `SUMMARY_EMAIL_TO`.

1. **Expected Output**:

   - **Agent A Terminal**: "Verified muhammadtaha7579@gmail.com: Y", then "No new leads to verify."
   - **Agent B Terminal**: "Outreach to muhammadtaha7579@gmail.com: Sent/No Response", then "No new verified leads to contact."
   - **Server Terminal**: Logs for `/respond` requests (e.g., "GET /respond?lead_id=3&response=interested").
   - **Supervisor Terminal**:

     ```
     Total Leads: 3, Verified: 2, Interested: 1, Not Interested: 1, No Response: 0, Pending: False
     Summary email sent: HTTP 202
     ```
   - **Emails**: Outreach emails in lead inboxes, summary email in `SUMMARY_EMAIL_TO`.


## Notes

- The system :
  - Processes leads from a Google Sheet.
  - Verifies emails (Agent A).
  - Sends outreach emails and captures responses via links (Agent B).
  - Consolidates results and sends summary emails (Supervisor).