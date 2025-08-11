import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet_data_kp():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_key.json", scope)
        client = gspread.authorize(creds)

        # Pastikan buka spreadsheet dan worksheet-nya
        spreadsheet = client.open("kenaikan_pangkat")
        print("Spreadsheet title:", spreadsheet.title)

        sheet = spreadsheet.worksheet("Sheet1")
        print("Worksheet title:", sheet.title)

        records = sheet.get_all_records()
        print("Jumlah baris:", len(records))

        return records

    except Exception as e:
        print("Gagal membaca Google Sheets:", e)
        return []