import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

# Define variables
SCOPES = ['https://www.googleapis.com/auth/indexing', 'https://www.googleapis.com/auth/webmasters']
SERVICE_ACCOUNT_FILE = 'api_key.json'  # Replace with the actual path to your JSON key
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

# Function to notify Google
def notify_google(url, action):
    # Define the API endpoint
    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    # Define the request body
    body = {
        "url": url,
        "type": action  # "URL_UPDATED" or "URL_DELETED"
    }

    # Get an access token from the credentials
    access_token = credentials.token  # Fetch the token directly
    if not access_token:  # If the token is expired or not fetched yet
        credentials.refresh(Request())  # Refresh the credentials
        access_token = credentials.token

    # Set the headers with the Bearer Token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(endpoint, json=body, headers=headers)

    # Handle the response
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

    # Extract URLs from <loc> tags
    urls = [url.text for url in root.findall(".//ns:loc", namespace)]

    # Send update or delete notifications for each URL
    for url in urls:
        print(f"Processing URL: {url}")
        notify_google(url, "URL_UPDATED")  # Notify Google to update the URL
        #notify_google(url, "URL_DELETED")  # Use this line to notify deletion
else:
    print(f"Failed to fetch sitemap: {response.status_code}")

import requests
import json

def send_request(url, action):
    """
    Send a request to the Google Indexing API.
    
    Args:
        url (str): The URL to send.
        action (str): The type of request ("URL_UPDATED" or "URL_DELETED").
    """
    # Set the endpoint URL for the Indexing API
    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    # Define the request body
    body = {
        "url": url,
        "type": action  # "URL_UPDATED" or "URL_DELETED"
    }

    # Add authentication details (access token is needed)
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",  # Replace with a valid access token
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(endpoint, json=body, headers=headers)

    # Check the response
    if response.status_code == 200:
        print(f"Successfully notified Google for {action}: {url}")
    else:
        print(f"Failed to notify Google for {action}: {url}")
        print(f"Response: {response.status_code}, {response.text}")

def send_batch_requests(file_path):
    """
    Send batch requests to the Google Indexing API.
    
    Args:
        file_path (str): Path to the JSON file containing URL data.
    """
    # Read the URLs from the JSON file
    with open(file_path, 'r') as file:
        urls = json.load(file)
    
    # Send individual requests for each URL
    for entry in urls:
        send_request(entry['url'], entry['type'])