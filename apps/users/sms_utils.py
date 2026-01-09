"""
SMS Utility Functions
Tasdiqlash kodlarini generate qilish va yuborish uchun yordamchi funksiyalar
"""

import random
import logging
from django.utils import timezone
from .models import PhoneOTP
from .services import send_sms, send_registration_success_sms

logger = logging.getLogger(__name__)


def generate_verification_code():
    """
    6 raqamli tasdiqlash kodini generate qilish

    Returns:
        str: 6 raqamli kod (masalan: "123456")
    """
    return str(random.randint(100000, 999999))


def send_verification_code(phone):
    """
    Telefon raqamiga tasdiqlash kodi yuborish

    Args:
        phone (str): Telefon raqami (+998XXXXXXXXX formatida)

    Returns:
        dict: {
            'success': bool,
            'code': str or None,
            'message': str
        }
    """
    try:
        # Avvalgi foydalanilmagan kodlarni o'chirish
        PhoneOTP.objects.filter(phone=phone, is_used=False).update(is_used=True)

        # Yangi kod yaratish
        code = generate_verification_code()

        # Bazaga saqlash
        PhoneOTP.objects.create(phone=phone, code=code)

        # SMS yuborish
        sms_sent = send_sms(phone, code)

        if sms_sent:
            logger.info(f"Tasdiqlash kodi yuborildi: {phone}")
            return {
                "success": True,
                "code": code,
                "message": "SMS kod muvaffaqiyatli yuborildi",
            }
        else:
            logger.error(f"SMS yuborishda xatolik: {phone}")
            return {
                "success": False,
                "code": None,
                "message": "SMS yuborishda xatolik yuz berdi",
            }

    except Exception as e:
        logger.error(f"Tasdiqlash kodi yuborishda xatolik: {e}")
        return {"success": False, "code": None, "message": f"Xatolik: {str(e)}"}


def verify_code(phone, code):
    """
    Tasdiqlash kodini tekshirish

    Args:
        phone (str): Telefon raqami
        code (str): Foydalanuvchi kiritgan kod

    Returns:
        dict: {
            'valid': bool,
            'message': str,
            'expired': bool,
            'used': bool
        }
    """
    try:
        # Eng yangi kodini topish
        otp = (
            PhoneOTP.objects.filter(phone=phone, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return {
                "valid": False,
                "message": "Kod noto'g'ri yoki allaqachon ishlatilgan",
                "expired": False,
                "used": True,
            }

        # Muddati tugaganligini tekshirish
        if otp.is_expired():
            otp.is_used = True
            otp.save()
            return {
                "valid": False,
                "message": "Kodning muddati tugagan. Yangi kod so'rang",
                "expired": True,
                "used": False,
            }

        # Kod to'g'ri
        otp.is_used = True
        otp.save()

        return {
            "valid": True,
            "message": "Kod tasdiqlandi",
            "expired": False,
            "used": False,
        }

    except Exception as e:
        logger.error(f"Kodni tekshirishda xatolik: {e}")
        return {
            "valid": False,
            "message": f"Xatolik: {str(e)}",
            "expired": False,
            "used": False,
        }


def notify_new_user_registered(phone, user_name=None):
    """
    Yangi foydalanuvchi ro'yxatdan o'tganda SMS yuborish

    Args:
        phone (str): Telefon raqami
        user_name (str, optional): Foydalanuvchi ismi

    Returns:
        bool: SMS yuborilgan bo'lsa True, aks holda False
    """
    try:
        result = send_registration_success_sms(phone, user_name)
        if result:
            logger.info(f"Ro'yxatdan o'tish SMS yuborildi: {phone}")
        return result
    except Exception as e:
        logger.error(f"Ro'yxatdan o'tish SMS yuborishda xatolik: {e}")
        return False


def resend_verification_code(phone):
    """
    Tasdiqlash kodini qayta yuborish

    Bu funksiya avvalgi foydalanilmagan kodlarni bekor qiladi
    va yangi kod yuboradi.

    Args:
        phone (str): Telefon raqami

    Returns:
        dict: send_verification_code() ning natijasi
    """
    logger.info(f"Tasdiqlash kodi qayta yuborilmoqda: {phone}")
    return send_verification_code(phone)


def get_active_verification_code(phone):
    """
    Telefon raqami uchun aktiv (foydalanilmagan va muddati tugamagan)
    tasdiqlash kodini olish

    Args:
        phone (str): Telefon raqami

    Returns:
        PhoneOTP or None: Aktiv kod obyekti yoki None
    """
    otp = (
        PhoneOTP.objects.filter(phone=phone, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if otp and not otp.is_expired():
        return otp
    return None


def clean_expired_codes():
    """
    Muddati tugagan va foydalanilmagan kodlarni tozalash

    Bu funksiyani periodic task sifatida ishlatish mumkin
    (masalan: Celery beat bilan)

    Returns:
        int: Tozalangan kodlar soni
    """
    expired_threshold = timezone.now() - timezone.timedelta(minutes=5)

    count = PhoneOTP.objects.filter(
        is_used=False, created_at__lt=expired_threshold
    ).update(is_used=True)

    logger.info(f"Tozalangan kodlar soni: {count}")
    return count
