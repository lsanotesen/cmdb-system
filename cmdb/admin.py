from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Idc, Host, Cabinet, HostGroup, IpSource, BastionHost, Module, Role, UserProfile


class HostInline(admin.TabularInline):
    model = Cabinet.serverList.through
    extra = 1


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户扩展信息'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'get_real_name', 'get_role')

    def get_real_name(self, obj):
        return obj.userprofile.real_name if hasattr(obj, 'userprofile') and obj.userprofile.real_name else '-'
    get_real_name.short_description = '真实姓名'

    def get_role(self, obj):
        return obj.userprofile.role.name if hasattr(obj, 'userprofile') and obj.userprofile.role else '-'
    get_role.short_description = '角色'


@admin.register(Idc)
class IdcAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'operator', 'memo')
    search_fields = ('name', 'area', 'operator')
    list_filter = ('area', 'operator')


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'ip', 'idc', 'asset_type', 'status', 'os')
    search_fields = ('hostname', 'ip')
    list_filter = ('asset_type', 'status', 'idc')
    raw_id_fields = ('idc',)


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ('name', 'idc', 'desc')
    search_fields = ('name',)
    filter_horizontal = ('serverList',)


@admin.register(HostGroup)
class HostGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc')
    search_fields = ('name',)
    filter_horizontal = ('serverList',)


@admin.register(IpSource)
class IpSourceAdmin(admin.ModelAdmin):
    list_display = ('ip', 'ip_segment', 'switch_name')
    search_fields = ('ip',)


@admin.register(BastionHost)
class BastionHostAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'username', 'is_enabled')
    search_fields = ('name', 'host')
    list_filter = ('is_enabled',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'real_name', 'role', 'department', 'phone')
    search_fields = ('user__username', 'real_name')
    list_filter = ('role', 'department')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
