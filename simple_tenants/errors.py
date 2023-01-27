from django.http import Http404


class TenantNotSetError(Exception):
    pass


class TenantNotFoundError(Http404):
    pass
