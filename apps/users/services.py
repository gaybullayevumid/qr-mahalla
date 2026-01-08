import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EskizSMSService:
    """Eskiz SMS API xizmati"""

    def __init__(self):
        self.api_url = settings.ESKIZ_API_URL
        self.email = settings.ESKIZ_EMAIL
        self.password = settings.ESKIZ_PASSWORD
        self.from_number = settings.ESKIZ_FROM
        self.token = None

    def get_token(self):
        """Eskiz API dan token olish"""
        try:
            url = f"{self.api_url}/auth/login"
            payload = {"email": self.email, "password": self.password}
            response = requests.post(url, data=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("data", {}).get("token")
                logger.info("Eskiz token muvaffaqiyatli olindi")
                return self.token
            else:
                logger.error(f"Eskiz token olishda xato: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Eskiz token olishda xato: {e}")
            return None

    def send_sms(self, phone, message):
        """Eskiz orqali SMS yuborish"""
        try:
            # Agar token bo'lmasa, yangi token olamiz
            if not self.token:
                self.get_token()

            if not self.token:
                logger.error("Eskiz token yo'q, SMS yuborib bo'lmaydi")
                return False

            # Telefon raqamini formatlash (faqat raqamlar)
            phone_clean = "".join(filter(str.isdigit, phone))

            url = f"{self.api_url}/message/sms/send"
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "mobile_phone": phone_clean,
                "message": message,
                "from": self.from_number,
            }

            response = requests.post(url, data=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"SMS muvaffaqiyatli yuborildi: {phone}")
                return True
            elif response.status_code == 401:
                # Token muddati tugagan, yangi token olamiz va qayta urinib ko'ramiz
                logger.warning("Eskiz token muddati tugagan, yangilanmoqda...")
                self.get_token()
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                    response = requests.post(
                        url, data=payload, headers=headers, timeout=10
                    )
                    if response.status_code == 200:
                        logger.info(
                            f"SMS muvaffaqiyatli yuborildi (2-urinish): {phone}"
                        )
                        return True

            logger.error(
                f"SMS yuborishda xato: {response.status_code} - {response.text}"
            )
            return False

        except Exception as e:
            logger.error(f"SMS yuborishda xato: {e}")
            return False


def send_sms(phone, code):
    """
    Send SMS verification code via Eskiz SMS service.

    Args:
        phone: User's phone number
        code: 6-digit verification code

    Returns:
        bool: True if message was successfully sent, False otherwise
    """
    # SMS matni
    message = f"QR MAHALLA tizimiga kirish uchun tasdiqlash kodi: {code}\n\nKod 1.5 daqiqa davomida amal qiladi."

    try:
        eskiz = EskizSMSService()
        result = eskiz.send_sms(phone, message)

        if result:
            logger.info(f"SMS yuborildi (Eskiz): {phone} -> {code}")
            return True
        else:
            logger.error(f"SMS yuborishda xatolik: {phone}")
            return False

    except Exception as e:
        logger.error(f"SMS yuborishda xatolik: {e}")
        return False
