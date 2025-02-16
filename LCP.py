import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import time

URL = "https://gadinsider.com/"
API_KEY = "AIzaSyCLYiwz8BQfSiecUwKx0iCMZFVaxK4tEmw"
SERVICE_ACCOUNT_FILE = "D:\\downloadd\\Web Scrapping\\five-447908-a3e04cc38fab.json"
SHEET_NAME = "LCP-Data-Gadinsider"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def setup_google_sheets(service_account_file, sheet_name):
    creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def get_lcp_value(url, api_key, strategy):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}&strategy={strategy}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            field_data_ms = data.get('loadingExperience', {}).get('metrics', {}).get('LARGEST_CONTENTFUL_PAINT_MS', {}).get('percentile', None)
            lab_data_ms = data.get('lighthouseResult', {}).get('audits', {}).get('largest-contentful-paint', {}).get('numericValue', None)
            
            field_data = field_data_ms / 1000 if field_data_ms else None
            lab_data = lab_data_ms / 1000 if lab_data_ms else None
            return field_data, lab_data
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response content: {response.text}")
            return None, None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None

def log_lcp_data():
    sheet = setup_google_sheets(SERVICE_ACCOUNT_FILE, SHEET_NAME)

    while True:  
        desktop_field_lcp, desktop_lab_lcp = get_lcp_value(URL, API_KEY, strategy="desktop")
        mobile_field_lcp, mobile_lab_lcp = get_lcp_value(URL, API_KEY, strategy="mobile")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [
            [timestamp, "Desktop", desktop_field_lcp],
            [timestamp, "Mobile", mobile_field_lcp]
        ]
        sheet.append_rows(data)
        print(f"LCP data logged at {timestamp}")

        time.sleep(24 * 60 * 60)

if __name__ == "__main__":
    log_lcp_data()