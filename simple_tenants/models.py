from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.text import slugify

from .conf import conf
from .errors import TenantNotSetError
from .managers import TenantAwareManager
from .utils import get_current_tenant, tenant_context_disabled


class AbstractTenant(models.Model):

    prefix = models.CharField(max_length=15, unique=True, db_index=True)

    populate_prefix_from = "prefix"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.prefix = slugify(getattr(self, self.populate_prefix_from))

        super().save(*args, **kwargs)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(
        conf.SIMPLE_TENANTS_MODEL, on_delete=models.CASCADE, editable=False
    )

    objects = TenantAwareManager()
    unscoped = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            setattr(self, conf.SIMPLE_TENANTS_FIELD, get_current_tenant())

        super().save(*args, **kwargs)


class TenantAwareUserManager(UserManager, TenantAwareManager):
    pass


class TenantAwareAbstractUser(AbstractUser):
    tenant = models.ForeignKey(
        conf.SIMPLE_TENANTS_MODEL, on_delete=models.CASCADE, editable=False, null=True
    )

    objects = TenantAwareUserManager()
    unscoped = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            if self._state.adding:
                setattr(self, conf.SIMPLE_TENANTS_FIELD, get_current_tenant())
        except TenantNotSetError as e:
            if self.is_superuser:
                with tenant_context_disabled():
                    super().save(*args, **kwargs)
            else:
                raise e
        super().save(*args, **kwargs)
