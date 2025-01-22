import json

# Original JSON data
service_account_data = 'api_key.json'

# Converting the JSON to the required format
service_account_str = json.dumps(service_account_data).replace('"', '\\"')

# Forming the final string
final_string = f'SERVICE_ACCOUNT_KEY_JSON="{service_account_str}"'

# Output the result
print(final_string)
