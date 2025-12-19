import requests
from django.conf import settings


def send_sms(phone, code):
    """
    Send SMS code via Telegram bot
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN

        # Format message with code as monospace (easy to copy)
        message = f"""
🔐 QR Mahalla - Verification Code

Phone: <code>{phone}</code>
Code: <code>{code}</code>

This code will expire in 2 minutes.
"""

        # Try to send to all chat_ids if set
        chat_ids = getattr(settings, "TELEGRAM_CHAT_IDS", [])

        if chat_ids:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            success_count = 0

            for chat_id in chat_ids:
                chat_id = chat_id.strip()
                if not chat_id:
                    continue

                payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
                response = requests.post(url, json=payload, timeout=5)

                if response.status_code == 200:
                    print(f"✅ Telegram message sent to chat {chat_id}: {code}")
                    success_count += 1
                else:
                    print(f"❌ Failed to send to chat {chat_id}: {response.text}")

            if success_count > 0:
                print(
                    f"✅ Code sent to {success_count}/{len(chat_ids)} chats for {phone}"
                )
                return True
        else:
            print(f"⚠️ TELEGRAM_CHAT_IDS not set. Code: {code} for {phone}")
            print(f"📱 Send /start to bot: https://t.me/{bot_token.split(':')[0]}")

        # Fallback: print to console
        print(f"[SMS] {phone} -> Verification code: {code}")
        return False

    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        print(f"[SMS] {phone} -> Verification code: {code}")
        return False
