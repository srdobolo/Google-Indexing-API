import os
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
from dotenv import load_dotenv

# Step 3: Load API Key from Environment Variables
load_dotenv()  # Load environment variables from a .env file
SERVICE_ACCOUNT_KEY_JSON = os.getenv('API_KEY')

if not SERVICE_ACCOUNT_KEY_JSON:
    raise ValueError("The API_KEY environment variable is not set.")

# Write the API key to a temporary file
SERVICE_ACCOUNT_FILE = "temp_service_account.json"
with open(SERVICE_ACCOUNT_FILE, "w") as key_file:
    key_file.write(SERVICE_ACCOUNT_KEY_JSON)

# Define constants
SCOPES = ['https://www.googleapis.com/auth/indexing', 'https://www.googleapis.com/auth/webmasters']
SITEMAP_URL = 'https://www.smart-recruitments.com/sitemap.xml'
INDEXING_API_ENDPOINT = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

# Authenticate with Google API using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Refresh the credentials if the token is expired
if not credentials.valid:
    credentials.refresh(Request())

# Build the Search Console API client
webmasters_service = build('searchconsole', 'v1', credentials=credentials)

# Step 4: Notify Google Using the Loaded API Key
def notify_google(url, action):
    body = {
        "url": url,
        "type": action  # "URL_UPDATED" or "URL_DELETED"
    }

    access_token = credentials.token
    if not access_token:
        credentials.refresh(Request())
        access_token = credentials.token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(INDEXING_API_ENDPOINT, json=body, headers=headers)

    if response.status_code == 200:
        print(f"Successfully notified Google for {action}: {url}")
    else:
        print(f"Failed to notify Google for {action}: {url}")
        print(f"Response: {response.status_code}, {response.text}")

# Fetch and parse the sitemap
response = requests.get(SITEMAP_URL)
if response.status_code == 200:
    sitemap_xml = response.text
    root = ET.fromstring(sitemap_xml)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    urls = [url.text for url in root.findall(".//ns:loc", namespace)]

    for url in urls:
        print(f"Processing URL: {url}")
        notify_google(url, "URL_UPDATED")
else:
    print(f"Failed to fetch sitemap: {response.status_code}")

# Cleanup: Remove the temporary service account file
os.remove(SERVICE_ACCOUNT_FILE)