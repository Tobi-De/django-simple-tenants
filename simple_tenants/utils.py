from contextlib import contextmanager
from contextvars import ContextVar
from typing import Protocol, Any

from django.apps import apps
from django.db import models
from django.http import HttpRequest

from .conf import conf
from .exceptions import TenantNotSet

_local_tenant: ContextVar[str] = ContextVar("local_tenant_id")


def get_tenant_model() -> type[models.Model]:
    app_label, model_name = conf.TENANT_MODEL.split(".")
    return apps.get_model(app_label, model_name)  # type: ignore


def hostname_from_request(request: HttpRequest) -> str:
    return request.get_host().split(":")[0].lower()


def tenant_from_request(request: HttpRequest) -> models.Model:
    hostname = hostname_from_request(request)
    subdomain = hostname.split(".")[0]
    tenant_model = get_tenant_model()
    return tenant_model.objects.filter(subdomain=subdomain).first()


def get_current_tenant() -> models.Model:
    tenant_id = get_current_tenant_id()
    tenant_model = get_tenant_model()
    return tenant_model.objects.get(id=tenant_id)


def set_tenant(obj: models.Model) -> None:
    _local_tenant.set(str(obj.id))


def get_current_tenant_id():
    try:
        return _local_tenant.get()
    except LookupError as e:
        raise TenantNotSet(
            """
                Tenant is not set. Use `tenant_context`, to set the tenant before
                running any queries
                from simple_tenants import tenant_context
            """
        ) from e


@contextmanager
def tenant_content(obj: models.Model) -> None:
    token = _local_tenant.set(str(obj.id))
    try:
        yield
    finally:
        _local_tenant.reset(token)
