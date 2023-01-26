from django.contrib import admin
from django.http import HttpRequest

from .utils import tenant_from_request


class TenantAwareModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request: HttpRequest):
        queryset = super().get_queryset(request)
        tenant = tenant_from_request(request)
        queryset = queryset.filter(tenant=tenant)
        return queryset

    def save_model(self, request: HttpRequest, obj, *args, **kwargs):
        tenant = tenant_from_request(request)
        obj.tenant = tenant
        super().save_model(request, obj, *args, **kwargs)
