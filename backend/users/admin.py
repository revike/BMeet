from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import User, TemporaryBanIp, FriendRequest


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_display_links = ('id', 'username', 'email', 'first_name', 'last_name')
    fields = ('id', 'username', 'email', 'phone', 'friends', 'first_name',
              'last_name', 'activation_key', 'is_active', 'is_verify',
              'is_staff', 'is_superuser', 'date_joined', 'user_photo',)
    readonly_fields = ('id', 'date_joined',)


class TemporaryBanIpAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip_address', 'status', 'attempts', 'time_unblock')
    list_display_links = (
        'id', 'ip_address', 'status', 'attempts', 'time_unblock')
    search_fields = ('ip_address',)


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created')
    fields = (
        'from_user', 'to_user', 'created', 'message', 'is_active', 'is_except'
    )
    readonly_fields = ('created',)


admin.site.register(User, UserAdmin)
admin.site.register(TemporaryBanIp, TemporaryBanIpAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.unregister(Group)
admin.site.site_header = 'Админ-панель BMeet'
