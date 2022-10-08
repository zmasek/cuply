from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Microcontroller, Device, Profile, Plant, SnapShot
from mptt.admin import DraggableMPTTAdmin


@admin.register(SnapShot)
class SnapShotAdmin(admin.ModelAdmin):
    pass

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    pass


@admin.register(Microcontroller)
class MicrocontrollerAdmin(admin.ModelAdmin):
    pass


@admin.register(Device)
class DeviceAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'name',
        "pin",
    )
    list_display_links = (
        'name',
    )


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_token')
    list_select_related = ('profile', )

    def get_token(self, instance):
        return instance.profile.remote_token
    get_token.short_description = 'Remote Token'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
