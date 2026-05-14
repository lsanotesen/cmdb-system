from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='cmdb_index'),
    
    # 测试页面
    path('test/sidebar/', views.test_sidebar, name='test_sidebar'),

    # 登录/登出
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),

    # 用户管理
    path('settings/users/', views.user_management, name='user_management'),
    path('settings/user/add/', views.user_add, name='user_add'),
    path('settings/user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('settings/user/<int:user_id>/permissions/', views.user_permissions, name='user_permissions'),
    path('settings/user/<int:user_id>/disable/', views.user_disable, name='user_disable'),
    path('settings/user/<int:user_id>/enable/', views.user_enable, name='user_enable'),
    path('settings/user/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    # 角色管理
    path('settings/roles/', views.role_management, name='role_management'),

    # 权限管理
    path('settings/permissions/', views.permission_management, name='permission_management'),

    path('assets/', views.asset_list, name='asset_list'),
    path('asset/add/', views.asset_add, name='asset_add'),
    path('asset/<int:asset_id>/', views.asset_detail, name='asset_detail'),
    path('asset/<int:asset_id>/edit/', views.asset_edit, name='asset_edit'),
    path('asset/<int:asset_id>/delete/', views.asset_delete, name='asset_delete'),
    path('asset/batch/delete/', views.asset_batch_delete, name='asset_batch_delete'),
    path('asset/import/', views.import_assets_excel, name='asset_import'),
    path('idc/', views.idc_list, name='idc_list'),
    path('idc/add/', views.idc_add, name='idc_add'),
    path('idc/<int:idc_id>/edit/', views.idc_edit, name='idc_edit'),
    path('idc/<int:idc_id>/delete/', views.idc_delete, name='idc_delete'),
    path('cabinet/', views.cabinet_list, name='cabinet_list'),
    path('cabinet/add/', views.cabinet_add, name='cabinet_add'),
    path('cabinet/<int:cabinet_id>/edit/', views.cabinet_edit, name='cabinet_edit'),
    path('cabinet/<int:cabinet_id>/delete/', views.cabinet_delete, name='cabinet_delete'),
    path('group/', views.group_list, name='group_list'),
    path('group/add/', views.group_add, name='group_add'),
    path('group/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('group/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('export/excel/', views.export_assets_excel, name='export_assets_excel'),
    path('export/csv/', views.export_assets_csv, name='export_assets_csv'),
    path('api/hosts/', views.api_hosts, name='api_hosts'),

    path('server/', views.target_server_list, name='target_server_list'),
    path('server/add/', views.target_server_add, name='target_server_add'),
    path('server/<int:server_id>/edit/', views.target_server_edit, name='target_server_edit'),
    path('server/<int:server_id>/delete/', views.target_server_delete, name='target_server_delete'),
    path('server/batch/delete/', views.target_server_batch_delete, name='target_server_batch_delete'),
    path('server/export/', views.export_target_server_excel, name='export_target_server'),
    path('server/import/', views.import_target_server_excel, name='import_target_server'),

    path('bastion/', views.bastion_list, name='bastion_list'),
    path('bastion/add/', views.bastion_add, name='bastion_add'),
    path('bastion/<int:bastion_id>/edit/', views.bastion_edit, name='bastion_edit'),
    path('bastion/<int:bastion_id>/delete/', views.bastion_delete, name='bastion_delete'),

    path('collect/task/', views.collect_task_list, name='collect_task_list'),
    path('collect/task/add/', views.collect_task_add, name='collect_task_add'),
    path('collect/task/<int:task_id>/edit/', views.collect_task_edit, name='collect_task_edit'),
    path('collect/task/<int:task_id>/run/', views.run_collect_task, name='run_collect_task'),
    path('collect/task/<int:task_id>/immediate/', views.immediate_collect, name='immediate_collect'),
    path('collect/task/<int:task_id>/restart/', views.restart_collect_task, name='restart_collect_task'),
    path('collect/task/<int:task_id>/delete/', views.collect_task_delete, name='collect_task_delete'),
    path('collect/progress/<str:progress_file>/', views.collect_task_progress, name='collect_task_progress'),
    path('collect/history/', views.collect_history, name='collect_history'),
    path('collect/task/<int:task_id>/stop/', views.stop_collect_task, name='stop_collect_task'),

    path('batch/command/', views.batch_command_list, name='batch_command_list'),
    path('batch/command/add/', views.batch_command_add, name='batch_command_add'),
    path('batch/command/<int:command_id>/edit/', views.batch_command_edit, name='batch_command_edit'),
    path('batch/command/<int:command_id>/run/', views.run_batch_command, name='run_batch_command'),
    path('batch/command/<int:command_id>/stop/', views.stop_batch_command, name='stop_batch_command'),
    path('batch/command/<int:command_id>/delete/', views.batch_command_delete, name='batch_command_delete'),
    path('batch/command/progress/<str:progress_file>/', views.batch_command_progress, name='batch_command_progress'),

    # 静态资产相关路由
    path('static/assets/', views.static_asset_list, name='static_asset_list'),
    path('static/asset/add/', views.static_asset_add, name='static_asset_add'),
    path('static/asset/<int:asset_id>/edit/', views.static_asset_edit, name='static_asset_edit'),
    path('static/asset/<int:asset_id>/delete/', views.static_asset_delete, name='static_asset_delete'),
    path('static/asset/batch/delete/', views.static_asset_batch_delete, name='static_asset_batch_delete'),
    path('static/asset/import/', views.static_asset_import, name='static_asset_import'),
    path('static/export/excel/', views.export_static_assets_excel, name='export_static_assets_excel'),
    path('static/export/csv/', views.export_static_assets_csv, name='export_static_assets_csv'),
    
    # 机柜布局图
    path('cabinet/layout/', views.cabinet_layout, name='cabinet_layout'),
    path('api/assets/', views.api_assets, name='api_assets'),
    
    # 数据备份
    path('backup/', views.backup_list, name='backup_list'),
    path('backup/list/', views.get_backup_list_with_stats, name='backup_list_api'),
    path('backup/create/', views.create_database_backup, name='create_backup'),
    path('backup/delete/<str:filename>/', views.delete_backup, name='delete_backup'),
    path('backup/download/<str:filename>/', views.download_backup, name='download_backup'),
    path('backup/restore/<str:filename>/', views.restore_database_backup, name='restore_backup'),
    path('backup/database_restore/', views.database_restore, name='database_restore'),
    path('backup/config/', views.get_backup_config_api, name='get_backup_config'),
    path('backup/config/save/', views.save_backup_config_api, name='save_backup_config'),

    # 备件管理
    path('spareparts/', views.spareparts_list, name='spareparts_list'),
    path('spareparts/add/', views.spareparts_add, name='spareparts_add'),
    path('spareparts/<int:sparepart_id>/edit/', views.spareparts_edit, name='spareparts_edit'),
    path('spareparts/<int:sparepart_id>/delete/', views.spareparts_delete, name='spareparts_delete'),
    
    # 备件类型管理
    path('spareparts/types/', views.sparepart_types_list, name='sparepart_types_list'),
    path('spareparts/type/add/', views.sparepart_type_add, name='sparepart_type_add'),
    path('spareparts/type/<int:type_id>/edit/', views.sparepart_type_edit, name='sparepart_type_edit'),
    path('spareparts/type/<int:type_id>/delete/', views.sparepart_type_delete, name='sparepart_type_delete'),
]