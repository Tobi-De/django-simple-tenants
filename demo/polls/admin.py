from django.contrib import admin

from .models import Choice, Poll, Vote, User
from simple_tenants.admin import TenantAwareModelAdmin


@admin.register(Poll)
class PollAdmin(TenantAwareModelAdmin):
    fields = ["question", "created_by", "pub_date", "file"]
    readonly_fields = ["pub_date"]


admin.site.register(Choice)
admin.site.register(Vote)
admin.site.register(User)
