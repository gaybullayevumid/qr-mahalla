import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(phone, code):
    """
    Send SMS verification code via Telegram bot.

    Args:
        phone: User's phone number
        code: 6-digit verification code

    Returns:
        bool: True if message was successfully sent to at least one chat,
              False otherwise

    Note:
        Sends to all configured TELEGRAM_CHAT_IDS in settings.
        Falls back to logging if Telegram delivery fails.
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN

        message = f"""
🔐 QR Mahalla - Verification Code

Phone: <code>{phone}</code>
Code: <code>{code}</code>

⏱️ This code is valid for 1.5 minutes and can only be used once.
⚠️ Code cannot be reused after verification!
"""

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
                    logger.info(f"Telegram message sent to chat {chat_id}: {code}")
                    success_count += 1
                else:
                    logger.error(f"Failed to send to chat {chat_id}: {response.text}")

            if success_count > 0:
                logger.info(
                    f"Code sent to {success_count}/{len(chat_ids)} chats for {phone}"
                )
                return True
        else:
            logger.warning(f"TELEGRAM_CHAT_IDS not set. Code: {code} for {phone}")

        logger.info(f"[SMS] {phone} -> Verification code: {code}")
        return False

    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        logger.info(f"[SMS] {phone} -> Verification code: {code}")
        return False
