# scripts/auth_google.py
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

# Workspace Scopes (Gmail, Calendar, Drive, Docs, Sheets, Contacts, Tasks)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/tasks.readonly",
]

credentials_path = Path("secrets/credentials.json")
token_path = Path("secrets/token.json")

flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
creds = flow.run_local_server(port=0)

token_path.write_text(creds.to_json())
print(f"Success! token.json generated at {token_path}")