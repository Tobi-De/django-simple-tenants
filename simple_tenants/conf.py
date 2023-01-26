from __future__ import annotations

from django.conf import settings

from django.conf import settings
from django.urls import reverse


class Settings:
    """
    Shadow Django's settings with a little logic
    """

    @property
    def TENANT_MODEL(self) -> str:
        return getattr(settings, "TENANT_MODEL")

    @property
    def TENANT_EXCLUDE_URLS(self) -> list[str]:
        return getattr(settings, "TENANT_EXCLUDE_URLS", [reverse("admin:login")])


conf = Settings()
