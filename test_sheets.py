import gspread
from google.oauth2.service_account import Credentials

# Tentukan scope
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Load credentials.json
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)

# Authorize client
client = gspread.authorize(creds)

# Buka spreadsheet
sheet = client.open("DataWebsite").sheet1

# Ambil semua data
records = sheet.get_all_records()
print(records)
