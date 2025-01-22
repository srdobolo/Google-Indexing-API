import base64

# Replace 'api_key.json' with the path to your JSON file
with open('api_key.json', 'rb') as f:
    encoded_key = base64.b64encode(f.read()).decode()

print(f"Encoded API key:\n{encoded_key}")