import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
SHEET_ID = os.getenv('SHEET_ID')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
SUMMARY_EMAIL_TO = os.getenv('SUMMARY_EMAIL_TO')
BASE_URL = os.getenv('BASE_URL')