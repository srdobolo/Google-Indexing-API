import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
SCOPES = ['https://www.googleapis.com/auth/indexing', 'https://www.googleapis.com/auth/webmasters']
SERVICE_ACCOUNT_FILE = "api_key.json"  # Replace with your JSON key path
SITEMAP_URL = "https://www.smart-recruitments.com/sitemap.xml"
INDEXING_API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# Authenticate with Google API
def authenticate_with_google():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials

# Notify Google about a URL
def notify_google(credentials, url, action):
    body = {
        "url": url,
        "type": action  # "URL_UPDATED" or "URL_DELETED"
    }

    if not credentials.valid:
        credentials.refresh(Request())

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    response = requests.post(INDEXING_API_ENDPOINT, json=body, headers=headers)
    if response.status_code == 200:
        logging.info(f"Successfully notified Google for {action}: {url}")
    else:
        logging.error(f"Failed to notify Google for {action}: {url}")
        logging.error(f"Response: {response.status_code}, {response.text}")

# Fetch and parse sitemap
def fetch_sitemap_urls(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [url.text for url in root.findall(".//ns:loc", namespace)]
    else:
        logging.error(f"Failed to fetch sitemap: {response.status_code}")
        return []

# Main function
def main():
    credentials = authenticate_with_google()
    urls = fetch_sitemap_urls(SITEMAP_URL)

    if not urls:
        logging.error("No URLs found in the sitemap.")
        return

    for url in urls:
        logging.info(f"Processing URL: {url}")
        notify_google(credentials, url, "URL_UPDATED")

if __name__ == "__main__":
    main()