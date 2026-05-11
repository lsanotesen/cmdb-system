from django import template

register = template.Library()

@register.filter(name='has_permission')
def has_permission(user, permission_code):
    if user is None or not user.is_authenticated:
        return False
    
    if hasattr(user, 'userprofile'):
        return user.userprofile.has_permission(permission_code)
    
    return False

@register.filter(name='has_module_permission')
def has_module_permission(user, module_code):
    if user is None or not user.is_authenticated:
        return False
    
    # 超级管理员自动拥有所有模块的访问权限
    if user.is_superuser:
        return True
    
    if hasattr(user, 'userprofile'):
        # 模块显示只检查 view 权限
        return user.userprofile.has_permission(f"{module_code}_view")
    
    return False
