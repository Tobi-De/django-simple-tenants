from .utils import set_tenant, tenant_from_request


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = tenant_from_request(request)
        set_tenant(tenant)
        request.tenant = tenant
        response = self.get_response(request)
        return response
