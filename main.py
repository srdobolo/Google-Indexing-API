import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Setup logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # For console output
        logging.FileHandler("app.log", mode="w")  # For file logging
    ]
)

# Constants
SCOPES = ['https://www.googleapis.com/auth/indexing', 'https://www.googleapis.com/auth/webmasters']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "api_key.json")
SITEMAP_URL = os.getenv("SITEMAP_URL", "https://www.smart-recruitments.com/sitemap.xml")
INDEXING_API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# Authenticate with Google API
def authenticate_with_google():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    if not credentials.valid:
        credentials.refresh(Request())
    # Retry logic for potential network issues
    for _ in range(3):
        try:
            if credentials.valid:
                return credentials
            credentials.refresh(Request())
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            time.sleep(2)
    logging.error("Authentication failed after multiple attempts.")
    raise Exception("Failed to authenticate with Google API.")

# Notify Google about a URL
def notify_google(credentials, url, action):
    body = {"url": url, "type": action}
    headers = {"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json"}

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.post(INDEXING_API_ENDPOINT, json=body, headers=headers, timeout=10)
            response.raise_for_status()  # Raise error for failed requests
            logging.info(f"Successfully notified Google for {action}: {url}")
            return
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to notify Google for {action}: {url} - {e}")
            time.sleep(2)  # Wait before retrying
    logging.error(f"Failed to notify Google for {action}: {url} after 3 attempts.")

# Fetch and parse sitemap
def fetch_sitemap_urls(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)  # Timeout set to 10 seconds
        response.raise_for_status()  # Raise an error for non-2xx status codes
        root = ET.fromstring(response.text)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [url.text for url in root.findall(".//ns:loc", namespace)]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch sitemap: {e}")
        return []

def process_urls(urls, credentials):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(notify_google, credentials, url, "URL_UPDATED"): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()  # This will raise any exceptions caught in notify_google
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")

# Main function
def main():
    try:
        credentials = authenticate_with_google()
        urls = fetch_sitemap_urls(SITEMAP_URL)
        if not urls:
            logging.error("No URLs found in the sitemap.")
            sys.exit(1)  # Exit with error code 1 if no URLs found

        process_urls(urls, credentials)
        logging.info("All URLs processed successfully.")
        sys.exit(0)  # Exit with success code 0

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit with error code 1 in case of failure

if __name__ == "__main__":
    main()