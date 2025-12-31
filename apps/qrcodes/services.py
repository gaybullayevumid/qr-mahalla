from typing import Optional


def get_client_ip(request) -> Optional[str]:
    """
    Extract client IP address from request.

    Checks X-Forwarded-For header first (for proxy/load balancer setups),
    falls back to REMOTE_ADDR if not available.

    Args:
        request: Django/DRF request object

    Returns:
        Client IP address as string, or None if not found
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")
