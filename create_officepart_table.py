import os
import pymysql

# 从环境变量获取数据库配置
db_name = os.environ.get('DB_NAME', 'cmdb')
db_user = os.environ.get('DB_USER', 'cmdb')
db_password = os.environ.get('DB_PASSWORD', 'cmdb123')
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = int(os.environ.get('DB_PORT', '3308'))

try:
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # 删除旧表（如果存在）
    cursor.execute('DROP TABLE IF EXISTS cmdb_officepart')
    
    # 创建办公机配件表
    cursor.execute('''
        CREATE TABLE cmdb_officepart (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(20) DEFAULT 'other',
            brand VARCHAR(100),
            model VARCHAR(100),
            serial_number VARCHAR(100) UNIQUE,
            source_computer VARCHAR(200),
            status VARCHAR(20) DEFAULT 'in_stock',
            dismantle_date DATE,
            location VARCHAR(200),
            purchase_date DATE,
            remark TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_category (category),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    conn.commit()
    print("Successfully created cmdb_officepart table")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()