from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils.text import slugify

from .conf import conf
from .errors import TenantNotSetError
from .managers import TenantAwareManager
from .utils import get_current_tenant, tenant_context_disabled


# todo: excludes some url
# and easy way to create first tenant
# maybe commands


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


class TenantAwareUserManager(UserManager, TenantAwareManager):
    pass


class TenantAwareAbstractUser(AbstractUser):
    tenant = models.ForeignKey(
        conf.TENANT_MODEL, on_delete=models.CASCADE, editable=False, null=True
    )

    objects = TenantAwareUserManager()
    unscoped = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            if self._state.adding:
                self.tenant = get_current_tenant()
        except TenantNotSetError:
            if self.is_superuser:
                with tenant_context_disabled():
                    super().save(*args, **kwargs)
            else:
                super().save(*args, **kwargs)
