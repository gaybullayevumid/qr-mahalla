import requests

# Test scan endpoint without auth
url = "http://192.168.0.126:8000/api/qrcodes/scan/65eb5437b84b4fc9/"

print(f"Testing: {url}")
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response:\n{response.text[:500]}")

if response.status_code == 200:
    import json

    print("\n✅ Success!")
    print(json.dumps(response.json(), indent=2))
