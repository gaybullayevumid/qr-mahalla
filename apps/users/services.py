import requests
from django.conf import settings


def send_sms(phone, code):
    """
    Send SMS code via Telegram bot
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN

        # Format message
        message = f"""
🔐 QR Mahalla - Verification Code

Phone: {phone}
Code: {code}

This code will expire in 2 minutes.
"""

        # Try to send to specific chat_id if set
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

        if chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            response = requests.post(url, json=payload, timeout=5)

            if response.status_code == 200:
                print(f"✅ Telegram message sent to {phone}: {code}")
                return True
            else:
                print(f"❌ Failed to send Telegram message: {response.text}")
        else:
            print(f"⚠️ TELEGRAM_CHAT_ID not set. Code: {code} for {phone}")
            print(f"📱 Send /start to bot: https://t.me/{bot_token.split(':')[0]}")

        # Fallback: print to console
        print(f"[SMS] {phone} -> Verification code: {code}")
        return False

    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        print(f"[SMS] {phone} -> Verification code: {code}")
        return False
