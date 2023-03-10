from simple_tenants.models import TenantAwareAbstractUser
from django.db import models
from simple_tenants.models import TenantAwareModel, AbstractTenant

from simple_tenants.utils import get_upload_path


class Tenant(AbstractTenant):
    name = models.CharField(max_length=100, unique=True)


class User(TenantAwareAbstractUser):
    pass


class Poll(TenantAwareModel):
    question = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now=True)
    file = models.ImageField(upload_to=get_upload_path, blank=True)

    def __str__(self):
        return self.question


class Choice(TenantAwareModel):
    poll = models.ForeignKey(Poll, related_name="choices", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=100)

    def __str__(self):
        return self.choice_text


class Vote(TenantAwareModel):
    choice = models.ForeignKey(Choice, related_name="votes", on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    voted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("poll", "voted_by")
