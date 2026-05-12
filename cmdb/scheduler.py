import os
import sys
import json
import gzip
from apscheduler import Scheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
from datetime import datetime

scheduler = None
schedule_id = None

def _init_django():
    """初始化Django环境"""
    os.chdir('/app')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmdb_project.settings')
    import django
    django.setup()

def create_database_backup_task():
    """执行数据库备份任务"""
    _init_django()
    from .models import BackupRecord
    config = get_backup_config()

    if not config.get('auto_backup_enabled', False):
        return

    backup_dir = config['backup_dir']
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'cmdb_db_backup_{timestamp}.sql.gz'
    filepath = os.path.join(backup_dir, filename)

    db_host = config['db_host']
    db_port = config['db_port']
    db_user = config['db_user']
    db_password = config['db_password']
    db_name = config['db_name']

    try:
        cmd = [
            'mysqldump',
            '-h', db_host,
            '-P', str(db_port),
            '-u', db_user,
            f'-p{db_password}',
            '--single-transaction',
            '--quick',
            '--skip-ssl',
            db_name
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            with gzip.open(filepath, 'wb') as f:
                f.write(result.stdout)
            BackupRecord.objects.create(
                backup_type='full',
                backup_name=filename,
                backup_path=filepath,
                status='success'
            )
            cleanup_old_backups(backup_dir, config.get('keep_count', 7), filename)
        else:
            BackupRecord.objects.create(
                backup_type='full',
                backup_name=filename,
                backup_path=filepath,
                status='failed',
                error_message=result.stderr.decode('utf-8', errors='ignore')
            )
    except Exception as e:
        BackupRecord.objects.create(
            backup_type='full',
            backup_name=filename,
            backup_path=filepath,
            status='failed',
            error_message=str(e)
        )

def cleanup_old_backups(backup_dir, keep_count, exclude_filename):
    """清理旧备份文件"""
    try:
        backup_files = []
        for f in os.listdir(backup_dir):
            if f.startswith('cmdb_db_backup_') and f.endswith('.sql.gz'):
                filepath = os.path.join(backup_dir, f)
                if os.path.isfile(filepath) and f != exclude_filename:
                    backup_files.append((os.path.getmtime(filepath), filepath))

        backup_files.sort(reverse=True)

        if len(backup_files) > keep_count:
            for mtime, filepath in backup_files[keep_count:]:
                os.remove(filepath)
    except Exception as e:
        print(f"清理旧备份失败: {str(e)}")

def get_backup_config():
    """获取备份配置"""
    config_file = '/data01/db_backup/backup_config.json'

    default_config = {
        'db_host': 'db',
        'db_port': 3306,
        'db_user': 'cmdb',
        'db_password': 'cmdb123',
        'db_name': 'cmdb',
        'backup_dir': '/data01/db_backup',
        'keep_count': 7,
        'auto_backup_enabled': False,
        'auto_backup_time': '02:00',
        'auto_backup_cron': '0 2 * * *'
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"读取备份配置失败: {str(e)}")

    return default_config

def update_scheduler_job():
    """更新定时任务"""
    global scheduler, schedule_id

    if scheduler is None:
        return

    if schedule_id:
        try:
            scheduler.remove_schedule(schedule_id)
            schedule_id = None
        except Exception as e:
            print(f"移除旧任务失败: {str(e)}")

    config = get_backup_config()
    if config.get('auto_backup_enabled', False):
        cron_expr = config.get('auto_backup_cron', '0 2 * * *')
        try:
            trigger = CronTrigger.from_crontab(cron_expr)
            schedule_id = scheduler.add_schedule(create_database_backup_task, trigger)
            print(f"定时任务添加成功: {schedule_id}")
        except Exception as e:
            print(f"添加定时任务失败: {str(e)}")

def start_scheduler():
    """启动任务调度器"""
    global scheduler

    if scheduler is not None:
        return

    scheduler = Scheduler()
    update_scheduler_job()
    scheduler.start_in_background()

def stop_scheduler():
    """停止任务调度器"""
    global scheduler

    if scheduler is not None:
        scheduler.stop()
        scheduler = None