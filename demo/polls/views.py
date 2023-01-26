from django.template.response import TemplateResponse

from .models import Poll


def index(request):
    return TemplateResponse(request, "index.html", {"polls": Poll.objects.all()})
