# Google Indexing API Automation Script

This Python script fetches URLs from an XML sitemap and automates the process of notifying Google about updates or deletions of these URLs using the Google Indexing API and Search Console API. The script handles authentication, processes URLs from the sitemap, and sends indexing requests to Google.

## Features

- Fetches URLs from an XML sitemap.
- Authenticates with Google APIs using a service account.
- Notifies Google of URL updates (`URL_UPDATED`) or deletions (`URL_DELETED`).
- Supports batch processing of URLs from a JSON file.

## Requirements

- Python 3.7 or higher
- Google Cloud Platform (GCP) service account with the following APIs enabled:
  - Google Indexing API
  - Google Search Console API

## Setup

1. **Clone the repository**  
   Clone this repository to your local machine:
   
```bash
git clone https://github.com/your-repo/google-indexing-automation.git
```

2. Install dependencies
Install the required Python libraries:

```bash
pip install requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

3. Set up Google Cloud Platform service account
- Create a service account in the GCP console.
- Download the JSON key file for the service account.
- Replace the (`SERVICE_ACCOUNT_FILE`) variable in the script with the path to your JSON key file.

4. Enable APIs
Ensure the following APIs are enabled in your GCP project:
- [Google Search Indexing API](https://console.cloud.google.com/apis/library/indexing.googleapis.com?inv=1&invt=Abm28Q)
- [Google Search Console API](https://console.cloud.google.com/apis/library/searchconsole.googleapis.com?inv=1&invt=Abm28Q)

5. Set the sitemap URL
Update de (`SITEMAP_URL`) variable with the URL of your sitemap.

# Usage
## Notify Google of URL Updates or Deletions
1. Run the script:
  ```bash
  python main.py
  ```

The script will:
- Fetch URLs from the sitemap.
- Notify Google of updates or deletions for each URL.

## Batch Processing URLs from a JSON File
1. Prepare a JSON file with URLs and actions in the following format:

```bash
[
    {"url": "https://example.com/page1", "type": "URL_UPDATED"},
    {"url": "https://example.com/page2", "type": "URL_DELETED"}
]
```

Call the (`send_batch_requests`) function with the path to your JSON file:

```bash
send_batch_requests("urls.json")
```

# Customization
To notify Google of deletions instead of updates, modify the (`notify_google`) function call:

```bash
notify_google(url, "URL_DELETED")
```

Update (`YOUR_ACCESS_TOKEN`) in the (`send_request`) function with a valid access token if not using service account credentials.

# Error Handling
- If the sitemap cannot be fetched, the script will display an error with the HTTP response code.
- If a URL notification fails, the script will log the response status and error details.

# License
This project is licensed under the MIT License. See the LICENSE file for details.
