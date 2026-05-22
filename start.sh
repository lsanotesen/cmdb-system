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

# 根据环境变量决定启动方式
if [ "$DEBUG" = "True" ]; then
    echo "Starting Django in development mode with auto-reload..."
    python3 manage.py runserver 0.0.0.0:8000
else
    echo "Starting Django in production mode with gunicorn..."
    gunicorn cmdb_project.wsgi:application --bind 0.0.0.0:8000 --timeout 300
fi