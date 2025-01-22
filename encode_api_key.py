import json
import os

# Original JSON data
service_account_data = 'api_key.json'

# Converting the JSON to the required format
service_account_str = json.dumps(service_account_data).replace('"', '\\"')

# Forming the final string
final_string = f'SERVICE_ACCOUNT_KEY_JSON="{service_account_str}"'

# Replace this with your actual encoded service account key
SERVICE_ACCOUNT_KEY_JSON = final_string

# Define the .env content
env_content = f"SERVICE_ACCOUNT_KEY_JSON={SERVICE_ACCOUNT_KEY_JSON}"

# Path to the temporary .env file
temp_env_path = ".env.temp"

# Write to the temporary .env file
with open(temp_env_path, "w") as env_file:
    env_file.write(env_content)

# After running your script, remember to delete the temporary .env file
