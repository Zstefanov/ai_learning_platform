import requests


# little file for testing any endpoint - subject to constant changes
url = "http://127.0.0.1:8000/debug-test"
response = requests.get(url)

if response.status_code == 200:
    print("Response:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")