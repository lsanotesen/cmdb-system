#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, '/app/cmdb_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmdb_project.settings')
django.setup()

from cmdb.models import Module, Role
from django.contrib.auth.models import User

def init_permissions():
    modules_data = [
        {'name': '资产管理', 'code': 'asset', 'order': 1},
        {'name': '静态资产', 'code': 'static_asset', 'order': 2},
        {'name': '主机管理', 'code': 'host', 'order': 3},
        {'name': '机柜管理', 'code': 'cabinet', 'order': 4},
        {'name': '机房管理', 'code': 'idc', 'order': 5},
        {'name': '资产组', 'code': 'group', 'order': 6},
        {'name': '堡垒机', 'code': 'bastion', 'order': 7},
        {'name': '目标服务器', 'code': 'server', 'order': 8},
        {'name': '批量命令', 'code': 'batch_command', 'order': 9},
        {'name': '采集任务', 'code': 'collect', 'order': 10},
        {'name': '数据库备份', 'code': 'backup', 'order': 11},
        {'name': '备件管理', 'code': 'sparepart', 'order': 12},
        {'name': '资产关系', 'code': 'asset_relation', 'order': 13},
        {'name': '生命周期', 'code': 'lifecycle', 'order': 14},
        {'name': '系统设置', 'code': 'settings', 'order': 15},
        {'name': '用户管理', 'code': 'user', 'order': 16},
        {'name': '角色管理', 'code': 'role', 'order': 17},
    ]

    for module_data in modules_data:
        module, created = Module.objects.get_or_create(
            code=module_data['code'],
            defaults=module_data
        )
        if created:
            print(f"创建模块: {module.name}")
        else:
            print(f"模块已存在: {module.name}")

    all_permissions = []
    for module in Module.objects.filter(is_active=True):
        for action in ['view', 'add', 'edit', 'delete', 'download']:
            all_permissions.append(f"{module.code}_{action}")

    admin_role, created = Role.objects.get_or_create(
        name='管理员',
        defaults={
            'description': '系统管理员，拥有所有权限',
            'permissions': all_permissions
        }
    )
    if created:
        print(f"创建角色: 管理员")
    else:
        admin_role.permissions = all_permissions
        admin_role.save()
        print(f"更新角色: 管理员")

    user_role, created = Role.objects.get_or_create(
        name='普通用户',
        defaults={
            'description': '普通用户，只有查看权限',
            'permissions': [
                'asset_view', 'asset_download',
                'host_view',
                'cabinet_view',
                'idc_view',
                'group_view',
                'backup_view',
            ]
        }
    )
    if created:
        print(f"创建角色: 普通用户")
    else:
        print(f"角色已存在: 普通用户")

    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('Admin1234')
        admin_user.save()
        print("创建管理员用户: admin")
    else:
        print("管理员用户已存在: admin")

    print("\n初始化完成!")
    print(f"共 {Module.objects.count()} 个模块")
    print(f"共 {Role.objects.count()} 个角色")
    print(f"共 {User.objects.count()} 个用户")

if __name__ == '__main__':
    init_permissions()