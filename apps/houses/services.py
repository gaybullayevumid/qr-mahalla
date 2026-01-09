import logging
import requests
from django.conf import settings
from datetime import datetime
from apps.users.services import EskizSMSService

logger = logging.getLogger(__name__)


def send_agent_house_notification(house):
    """
    Send notification when agent adds a house to the database.
    Sends both Telegram notification and SMS to owner if phone exists.

    Args:
        house: House instance that was just created by agent

    Returns:
        bool: True if message was successfully sent to at least one chat,
              False otherwise
    """
    try:
        # Send SMS to owner if phone exists
        if house.owner and house.owner.phone:
            try:
                sms_service = EskizSMSService()
                # Simple message matching approved template style
                message = f"Sizning uyingiz QR MAHALLA tizimiga qo'shildi."
                
                logger.info(f"Attempting to send SMS to house owner {house.owner.phone} for house ID: {house.id}")
                sms_sent = sms_service.send_sms(house.owner.phone, message)
                if sms_sent:
                    logger.info(
                        f"✅ SMS successfully sent to house owner {house.owner.phone} for house ID: {house.id}"
                    )
                else:
                    logger.warning(
                        f"❌ Failed to send SMS to house owner {house.owner.phone} for house ID: {house.id}"
                    )
            except Exception as e:
                logger.error(f"💥 Error sending SMS to house owner: {e}")
        else:
            logger.info(f"⚠️ No owner or phone number for house ID: {house.id}. SMS not sent.")

        # Continue with existing Telegram notification logic
        bot_token = settings.TELEGRAM_BOT_TOKEN

        # Get region, district, mahalla names
        mahalla = house.mahalla
        district = mahalla.district
        region = district.region

        # Format date
        sana = house.created_at.strftime("%d.%m.%Y %H:%M")

        message = f"""
🏘 Agent tomonidan uy qo'shildi

{region.name} viloyati, {district.name} tumani, {mahalla.name} mahallasida agent tomonidan uy bazaga qo'shildi.

🆔 ID: {house.id}
📅 Sana: {sana}
📍 Manzil: {house.address}
🏠 Uy raqami: {house.house_number or "Ko'rsatilmagan"}
👤 Egasi: {house.owner.get_full_name() if house.owner else "Ko'rsatilmagan"}
👨‍💼 Agent: created_by_agent

✅ Uy muvaffaqiyatli ro'yxatga olindi.
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
                    logger.info(f"Agent house notification sent to chat {chat_id}")
                    success_count += 1
                else:
                    logger.error(
                        f"Failed to send agent house notification to chat {chat_id}: {response.text}"
                    )

            if success_count > 0:
                logger.info(
                    f"Agent house notification sent to {success_count}/{len(chat_ids)} chats"
                )
                return True
        else:
            logger.warning(f"TELEGRAM_CHAT_IDS not set. House ID: {house.id}")

        logger.info(
            f"[Agent House Registration] House ID: {house.id}, Address: {house.address}"
        )
        return False

    except Exception as e:
        logger.error(f"Error sending agent house notification: {e}")
        logger.info(f"[Agent House Registration] House ID: {house.id}")
        return False


def send_house_registration_notification(house):
    """
    Send house registration notification via Telegram bot.

    Args:
        house: House instance that was just created

    Returns:
        bool: True if message was successfully sent to at least one chat,
              False otherwise

    Note:
        Sends to all configured TELEGRAM_CHAT_IDS in settings.
        Falls back to logging if Telegram delivery fails.
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN

        # Get region, district, mahalla names
        mahalla = house.mahalla
        district = mahalla.district
        region = district.region

        # Format date
        sana = house.created_at.strftime("%d.%m.%Y %H:%M")

        message = f"""
📢 Bildirishnoma

{region.name} viloyati, {district.name} tumani, {mahalla.name} mahallasida joylashgan uy davlat uy reyestriga kiritildi.

🆔 Identifikatsiya raqami: {house.id}
📅 Sana: {sana}
📍 Manzil: {house.address}
🏠 Uy raqami: {house.house_number or "Ko'rsatilmagan"}
👤 Egasi: {house.owner.get_full_name() if house.owner else "Ko'rsatilmagan"}

Ma'lumotlar to'g'riligini tekshirib chiqing.
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
                    logger.info(
                        f"House registration notification sent to chat {chat_id}"
                    )
                    success_count += 1
                else:
                    logger.error(
                        f"Failed to send house notification to chat {chat_id}: {response.text}"
                    )

            if success_count > 0:
                logger.info(
                    f"House registration notification sent to {success_count}/{len(chat_ids)} chats"
                )
                return True
        else:
            logger.warning(f"TELEGRAM_CHAT_IDS not set. House ID: {house.id}")

        logger.info(
            f"[House Registration] House ID: {house.id}, Address: {house.address}"
        )
        return False

    except Exception as e:
        logger.error(f"Error sending house registration notification: {e}")
        logger.info(f"[House Registration] House ID: {house.id}")
        return False
