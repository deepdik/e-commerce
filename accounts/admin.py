from django.contrib import admin


from .models import *

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserOtherInfoInline(admin.StackedInline):
    model = UserOtherInfo
    can_delete = False
    verbose_name_plural = 'UserOtherInfos'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserOtherInfoInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register([Role,Permission,UserPermissions])





