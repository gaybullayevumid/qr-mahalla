import requests
import json

url = "http://127.0.0.1:8000/api/qrcodes/scan/"
data = {"uuid": "df9dd4def795439b"}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
