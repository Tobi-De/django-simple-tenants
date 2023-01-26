from django.db import models

from .conf import conf
from .managers import TenantAwareManager
from .utils import get_current_tenant
from django.utils.text import slugify


class AbstractTenant(models.Model):

    subdomain = models.CharField(max_length=15, unique=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.subdomain = slugify(self.subdomain)

        super().save(*args, **kwargs)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(
        conf.TENANT_MODEL, on_delete=models.CASCADE, editable=False
    )

    objects = TenantAwareManager()
    unscoped = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.tenant = get_current_tenant()

        super().save(*args, **kwargs)
