import json
import os

# Path to your actual API key JSON file
service_account_file = 'api_key.json'

# Open the JSON file and load its content
with open(service_account_file, 'r') as f:
    service_account_data = json.load(f)

# Converting the JSON to a string and escaping necessary characters
service_account_str = json.dumps(service_account_data).replace('"', '\\"')

# Forming the final string
final_string = f'SERVICE_ACCOUNT_KEY_JSON="{service_account_str}"'

# Define the .env content
env_content = f"SERVICE_ACCOUNT_KEY_JSON={final_string}"

# Path to the temporary .env file
temp_env_path = ".env.temp"

# Write to the temporary .env file
with open(temp_env_path, "w") as env_file:
    env_file.write(env_content)

# After running your script, remember to delete the temporary .env file
