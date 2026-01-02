# Test Claim API
# 1. Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
  }'

# Copy token from response, then:

# 2. Claim QR Code
curl -X POST http://localhost:8000/api/qrcodes/10bfb53c26d34ad2/claim/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "first_name": "Frontend",
    "last_name": "User",
    "address": "Test Address from Curl",
    "house_number": "888",
    "mahalla": 1
  }'
