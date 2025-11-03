from __future__ import annotations

from django.conf import settings


def company_profile(request):
    """Expose company related settings to every template."""

    return {
        "COMPANY_NAME": getattr(settings, "COMPANY_NAME", "Mariana Nails"),
        "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", "contacto@example.com"),
        "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
        "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
        "WHATSAPP_URL": getattr(settings, "WHATSAPP_URL", ""),
    }
