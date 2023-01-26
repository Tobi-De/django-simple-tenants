from django.http import Http404

from .conf import conf
from .utils import set_tenant, tenant_from_request


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = tenant_from_request(request)
        # if not tenant and request.path not in conf.TENANT_EXCLUDE_URLS:
        #     raise Http404("Tenant not found")

        request.tenant = tenant
        set_tenant(tenant)
        response = self.get_response(request)
        return response
