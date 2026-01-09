import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _log_sms(phone, message, sms_type, user=None):
    """
    SMS yuborilishini log qilish.

    Args:
        phone: Telefon raqami
        message: SMS matni
        sms_type: SMS turi ('verification', 'registration', 'qr_scan', 'notification')
        user: Foydalanuvchi obyekti (optional)

    Returns:
        SMSLog obyekti
    """
    from .models_sms import SMSLog

    return SMSLog.objects.create(
        phone=phone, message=message, sms_type=sms_type, user=user, status="pending"
    )


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
    # SMS matni - Eskizda tasdiqlangan matn
    message = f"QR MAHALLA tizimiga kirish uchun tasdiqlash kodi: {code}"

    # Log yaratish
    sms_log = _log_sms(phone, message, "verification")

    try:
        eskiz = EskizSMSService()
        result = eskiz.send_sms(phone, message)

        if result:
            sms_log.mark_as_sent()
            logger.info(f"SMS yuborildi (Eskiz): {phone} -> {code}")
            return True
        else:
            sms_log.mark_as_failed("SMS yuborishda xatolik")
            logger.error(f"SMS yuborishda xatolik: {phone}")
            return False

    except Exception as e:
        sms_log.mark_as_failed(str(e))
        logger.error(f"SMS yuborishda xatolik: {e}")
        return False


def send_registration_success_sms(phone, user_name=""):
    """
    Send SMS after successful registration.

    Args:
        phone: User's phone number
        user_name: Optional user's name

    Returns:
        bool: True if message was successfully sent, False otherwise
    """
    # SMS matni - Eskizda tasdiqlangan matn
    message = "Siz QR MAHALLA tizimida muvaffaqiyatli ro'yxatdan o'tdingiz."

    # Log yaratish
    sms_log = _log_sms(phone, message, "registration")

    try:
        eskiz = EskizSMSService()
        result = eskiz.send_sms(phone, message)

        if result:
            sms_log.mark_as_sent()
            logger.info(f"Ro'yxatdan o'tish SMS yuborildi: {phone}")
            return True
        else:
            sms_log.mark_as_failed("SMS yuborishda xatolik")
            logger.error(f"Ro'yxatdan o'tish SMS yuborishda xatolik: {phone}")
            return False

    except Exception as e:
        sms_log.mark_as_failed(str(e))
        logger.error(f"Ro'yxatdan o'tish SMS yuborishda xatolik: {e}")
        return False


def send_qr_scan_sms(phone, qr_code):
    """
    Send SMS notification when QR code is scanned.

    Args:
        phone: User's phone number
        qr_code: QR code that was scanned

    Returns:
        bool: True if message was successfully sent, False otherwise
    """
    # SMS matni
    message = f"Sizning QR kodingiz muvaffaqiyatli skanerlandi.\n\nQR kod: {qr_code}"

    # Log yaratish
    sms_log = _log_sms(phone, message, "qr_scan")

    try:
        eskiz = EskizSMSService()
        result = eskiz.send_sms(phone, message)

        if result:
            sms_log.mark_as_sent()
            logger.info(f"QR kod skaner SMS yuborildi: {phone}")
            return True
        else:
            sms_log.mark_as_failed("SMS yuborishda xatolik")
            logger.error(f"QR kod skaner SMS yuborishda xatolik: {phone}")
            return False

    except Exception as e:
        sms_log.mark_as_failed(str(e))
        logger.error(f"QR kod skaner SMS yuborishda xatolik: {e}")
        return False
