import requests

# Test registration endpoint
url = "http://127.0.0.1:8000/api/users/auth/"

data = {"phone": "+998901234567"}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
