def send_sms(phone, code):
    """
    Keyinchalik bu yerga real SMS provider ulanadi:
    Eskiz / PlayMobile / Twilio
    """
    print(f"[SMS] {phone} -> Tasdiqlash kodi: {code}")
