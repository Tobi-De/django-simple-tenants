from __future__ import annotations

from django.conf import settings
from django.urls import reverse


class Settings:
    """
    Shadow Django's settings with a little logic
    """

    @property
    def SIMPLE_TENANTS_MODEL(self) -> str:
        return getattr(settings, "SIMPLE_TENANTS_MODEL")

    @property
    def SIMPLE_TENANTS_FIELD(self) -> str:
        return getattr(settings, "SIMPLE_TENANTS_FIELD", "tenant")


conf = Settings()
