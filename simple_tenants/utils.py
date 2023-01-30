from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import TypedDict

from django.apps import apps
from django.db import models
from django.http import HttpRequest
from django.utils import timezone

from .conf import conf
from .errors import TenantNotFoundError, TenantNotSetError


class TenantState(TypedDict):
    tenant_id: str | None
    enabled: bool


_local_tenant_state: ContextVar[TenantState] = ContextVar(
    "local_tenant_id", default={"tenant_id": None, "enabled": False}
)


def get_tenant_model() -> type[models.Model]:
    app_label, model_name = conf.SIMPLE_TENANTS_MODEL.split(".")
    return apps.get_model(app_label, model_name)  # type: ignore


def hostname_from_request(request: HttpRequest) -> str:
    return request.get_host().split(":")[0].lower()


def tenant_from_request(request: HttpRequest) -> models.Model:
    hostname = hostname_from_request(request)
    subdomain = hostname.split(".")[0]
    tenant_model = get_tenant_model()
    try:
        return tenant_model.objects.get(prefix=subdomain)
    except tenant_model.DoesNotExist:
        raise TenantNotFoundError(f"Tenant with subdomain {subdomain} not found")


def get_current_tenant() -> models.Model:
    tenant_id = get_current_tenant_id()
    tenant_model = get_tenant_model()
    return tenant_model.objects.get(id=tenant_id)


def set_tenant(obj: models.Model) -> None:
    _local_tenant_state.set({"tenant_id": str(obj.id), "enabled": True})  # type: ignore


def get_current_tenant_id() -> str:
    state = _local_tenant_state.get()
    if state["tenant_id"] is None:
        raise TenantNotSetError(
            "Tenant is required in context. Use `tenant_context`, "
            "to set the tenant before running any queries"
            " from simple_tenants import tenant_context"
        )
    return state["tenant_id"]


def is_tenant_disabled() -> bool:
    return _local_tenant_state.get()["enabled"] is False


@contextmanager
def tenant_context(obj: models.Model):
    token = _local_tenant_state.set({"tenant_id": str(obj.id), "enabled": True})  # type: ignore
    try:
        yield
    finally:
        _local_tenant_state.reset(token)


@contextmanager
def tenant_context_disabled():
    token = _local_tenant_state.set({"tenant_id": None, "enabled": False})
    try:
        yield
    finally:
        _local_tenant_state.reset(token)


def get_upload_path(instance, filename: str) -> str:
    str_date = timezone.now().date().strftime("%Y/%m/%d")
    return f"{instance.tenant.prefix}/{str_date}/{filename}"
