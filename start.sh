#!/bin/bash
set -e

# 等待数据库就绪
echo "Waiting for database to be ready..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "Database is ready. Starting Django..."

# 执行数据库迁移
python3 manage.py migrate --noinput

# 初始化权限数据
python3 init_permissions.py

# 启动 Django（设置 5 分钟超时，防止长时间操作被中断）
gunicorn cmdb_project.wsgi:application --bind 0.0.0.0:8000 --timeout 300