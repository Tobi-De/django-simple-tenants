from django.db.models import Manager, QuerySet

from .conf import conf
from .utils import get_current_tenant, get_current_tenant_id, is_tenant_disabled


class TenantAwareManager(Manager):
    def get_queryset(self):
        if is_tenant_disabled():
            return super().get_queryset()

        tenant_id = get_current_tenant_id()

        # If the manager was built from a queryset using
        # SomeQuerySet.as_manager() or SomeManager.from_queryset(),
        # we want to use that queryset instead of TenantAwareQuerySet.
        kwargs = {f"{conf.SIMPLE_TENANTS_FIELD}__id": tenant_id}
        if self._queryset_class != QuerySet:
            return super().get_queryset().filter(**kwargs)

        return TenantAwareQuerySet(self.model, using=self._db).filter(**kwargs)


class TenantAwareQuerySet(QuerySet):
    def bulk_create(self, objs, *args, **kwargs):
        for obj in objs:
            setattr(obj, conf.SIMPLE_TENANTS_FIELD, get_current_tenant())

        super().bulk_create(objs, *args, **kwargs)

    def as_manager(cls):
        manager = TenantAwareManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True

    as_manager = classmethod(as_manager)
