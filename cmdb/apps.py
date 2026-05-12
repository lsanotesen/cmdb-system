from django.apps import AppConfig


class CmdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'
    verbose_name = 'CMDB资产管理'
    
    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()