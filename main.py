import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Setup logging to both console and file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # For console output
        logging.FileHandler("app.log", mode="w")  # For file logging
    ]
)

# Constants
SCOPES = ['https://www.googleapis.com/auth/indexing']
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
SITEMAP_URL = os.getenv("SITEMAP_URL")
INDEXING_API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# Validate environment variables
if not GOOGLE_CREDENTIALS_JSON or not SITEMAP_URL:
    logging.error("Missing environment variables: GOOGLE_CREDENTIALS_JSON or SITEMAP_URL")
    sys.exit(1)

# Retry function to handle retries in both authenticate and notify functions
def retry_request(func, *args, retries=3, delay=2, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    logging.error(f"Failed after {retries} attempts.")
    raise Exception(f"Function {func.__name__} failed after {retries} attempts.")

# Authenticate with Google API using credentials written to a temp file
def authenticate_with_google():
    try:
        # Write the raw JSON string to a temporary file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as temp_file:
            temp_file.write(GOOGLE_CREDENTIALS_JSON)
            temp_file.flush()
            credentials = service_account.Credentials.from_service_account_file(
                temp_file.name, scopes=SCOPES
            )
        if not credentials.valid:
            request = Request()
            credentials.refresh(request)
        return credentials
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        raise

# Notify Google about a URL
def notify_google(session, credentials, url, action):
    body = {"url": url, "type": action}
    headers = {"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json"}

    try:
        response = session.post(INDEXING_API_ENDPOINT, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully notified Google for {action}: {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to notify Google for {action}: {url} - {e}")

# Fetch and parse sitemap
def fetch_sitemap_urls(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [url.text for url in root.findall(".//ns:loc", namespace)]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch sitemap: {e}")
        return []

# Notify all URLs from sitemap
def process_urls(urls, credentials):
    session = requests.Session()  # Reuse one session
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(notify_google, session, credentials, url, "URL_UPDATED"): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")

# Main execution
def main():
    try:
        credentials = authenticate_with_google()
        urls = fetch_sitemap_urls(SITEMAP_URL)
        if not urls:
            logging.error("No URLs found in the sitemap.")
            sys.exit(1)

        process_urls(urls, credentials)
        logging.info("All URLs processed successfully.")
        sys.exit(0)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()