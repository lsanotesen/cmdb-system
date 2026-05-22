# 资产管理系统 (CMDB)

基于 **Django 4.2 + MariaDB** 的企业级资产管理平台，提供主机管理、SSH配置管理、硬件信息自动采集、权限管理、机柜布局可视化等功能。

## ✨ 功能特性

### 🏭 资产管理
- **动态资产管理**
  - 主机列表、添加、编辑、删除
  - 支持 Excel 批量导入/导出
  - 主机详情查看（资产编号、机柜位置、部门、设备类型、IP地址、联系人、硬件配置等）
- **静态资产管理**
  - 静态资产列表、添加、编辑、删除
  - 支持批量导入/导出
  - 资产分组管理
- **动态资产组**
  - 资产组管理（添加、编辑、删除）
  - 支持按IP范围、标签等条件分组

### 🔐 SSH配置管理
- 批量导入SSH配置（支持Excel）
- 支持直连模式和跳板机模式
- 批量删除功能

### 🖥️ 硬件信息采集
- 通过SSH远程连接服务器自动采集硬件信息
- 支持跳板机跳转连接
- 采集内容：主机名、操作系统、CPU型号/数量、内存、硬盘、GPU、序列号、设备型号
- 支持定时采集和立即采集
- 实时采集进度追踪

### 🏢 机房管理
- 机房增删改查
- 机柜管理
- 主机组管理
- 机柜布局图可视化

### 📊 机柜布局图
- 可视化机柜布局展示
- 支持导出 Excel（带样式和布局图图片）
- 支持导出 HTML（保留完整样式）
- 支持导出 PNG 图片

### 👤 权限管理系统
- **用户管理**：添加、编辑、删除用户，修改密码
- **角色管理**：创建角色、分配权限
- **权限管理**：细粒度权限控制（查看、添加、编辑、删除、下载）
- **双角色系统**：管理员/普通用户模式，确保系统安全性

### 💾 数据备份
- 数据库备份
- 备份文件管理
- 数据恢复（支持上传SQL文件恢复，自动处理外键约束）
- 自动清理过期备份（可配置保留数量）

### 📦 备件管理
- 服务器备件管理
- 备件入库、出库、库存预警
- 备件类型管理

### 📋 生命周期管理
- 资产生命周期追踪
- 资产变更历史记录
- 资产维护记录

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose（推荐）
- 或 Python 3.10+ with Django 4.2

### 使用 Docker 部署

#### 1. 克隆项目

```bash
git clone https://github.com/lsanotesen/cmdb-system.git
cd cmdb-system
```

#### 2. 创建必要目录并设置权限

```bash
# 创建数据库数据目录
sudo mkdir -p /data01/mysql_data
# 创建数据库备份目录
sudo mkdir -p /data01/db_backup
# 设置目录权限
sudo chown -R 1000:1000 /data01/mysql_data
sudo chown -R 1000:1000 /data01/db_backup
sudo chmod -R 755 /data01/mysql_data
sudo chmod -R 755 /data01/db_backup

```

**说明**：
- `/data01/mysql_data`：用于存储数据库数据，容器内MariaDB运行用户ID为1000
- `/data01/db_backup`：用于存储数据库备份文件
- 请根据实际部署环境调整目录路径

#### 3. 启动服务

```bash
docker-compose up -d --build
```

**说明**：
- 首次启动需要使用 `--build` 参数构建镜像
- 数据库迁移和权限初始化会**自动执行**，无需手动操作
- 数据库数据持久化存储在 `/data01/mysql_data` 目录
- **重要**：请根据实际部署环境修改 `docker-compose.yml` 中的挂载目录路径，确保该目录存在且有写入权限

#### 4. 管理员账号

**默认管理员账号**（首次部署后**自动创建**）：
- 用户名：`admin`
- 密码：`Admin1234`

如需创建其他管理员账号，可执行：

```bash
docker-compose exec cmdb python3 manage.py createsuperuser
```

#### 5. 访问系统

```
系统访问地址: http://yourip:8001/cmdb/

```

### 使用 Python 直接运行

如果不使用 Docker，可以按照以下步骤部署：

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置数据库

编辑 `cmdb_project/settings.py`，修改数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cmdb',
        'USER': 'cmdb',
        'PASSWORD': 'cmdb123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### 3. 执行数据库迁移

```bash
python3 manage.py migrate
```

#### 4. 初始化权限数据

```bash
python3 init_permissions.py
```

#### 5. 创建管理员账号

```bash
python3 manage.py createsuperuser
```

#### 6. 启动服务

```bash
python3 manage.py runserver 0.0.0.0:8000
```

## 📁 项目结构

```
cmdb-system/
├── cmdb/                      # Django应用
│   ├── models.py             # 数据模型
│   ├── views.py              # 视图函数
│   ├── urls.py               # URL路由
│   ├── admin.py              # 管理后台配置
│   ├── forms.py              # 表单定义
│   ├── apps.py               # 应用配置
│   ├── migrations/           # 数据库迁移
│   └── templatetags/         # 自定义模板标签
│       └── custom_tags.py    # 权限检查标签
├── cmdb_project/             # Django项目配置
│   ├── settings.py           # 项目设置
│   ├── urls.py               # 主URL路由
│   └── wsgi.py               # WSGI配置
├── templates/                # 模板文件
│   ├── base.html             # 基础模板
│   ├── registration/         # 登录相关模板
│   └── cmdb/                 # CMDB页面模板
├── static/                   # 静态资源
│   ├── css/                  # 样式文件
│   ├── js/                   # JavaScript文件
│   └── images/               # 图片资源
├── docker-compose.yml         # Docker编排
├── Dockerfile                # Docker镜像配置
├── requirements.txt          # Python依赖
├── init_permissions.py       # 权限初始化脚本
├── manage.py                 # Django管理脚本
├── hw_collector.py           # 硬件采集脚本
└── README.md                 # 项目说明文档
```

## 🛠️ 技术栈

| 分类 | 技术 | 版本 |
|-----|------|-----|
| 后端框架 | Django | 4.2 |
| 数据库 | MariaDB | 10.11 |
| Web服务器 | Gunicorn | 21.x |
| 容器化 | Docker & Docker Compose | - |
| SSH连接 | Paramiko | 3.x |
| Excel处理 | openpyxl | 3.x |
| 前端框架 | Bootstrap | 5.x |
| JavaScript | jQuery | 3.x |

## 🔧 API接口

### 资产管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| `/cmdb/assets/` | GET | 资产列表 |
| `/cmdb/assets/add/` | GET/POST | 添加资产 |
| `/cmdb/assets/<id>/edit/` | GET/POST | 编辑资产 |
| `/cmdb/assets/<id>/delete/` | GET | 删除资产 |
| `/cmdb/assets/import/` | GET/POST | Excel导入 |
| `/cmdb/assets/export/excel/` | GET | Excel导出 |

### 静态资产
| 路径 | 方法 | 说明 |
|-----|------|-----|
| `/cmdb/static-assets/` | GET | 静态资产列表 |
| `/cmdb/static-assets/add/` | GET/POST | 添加静态资产 |
| `/cmdb/static-assets/<id>/edit/` | GET/POST | 编辑静态资产 |
| `/cmdb/static-assets/<id>/delete/` | GET | 删除静态资产 |

### 机房管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| `/cmdb/idc/` | GET | 机房列表 |
| `/cmdb/idc/add/` | GET/POST | 添加机房 |
| `/cmdb/idc/<id>/edit/` | GET/POST | 编辑机房 |
| `/cmdb/idc/<id>/delete/` | GET | 删除机房 |

### SSH配置
| 路径 | 方法 | 说明 |
|-----|------|-----|
| `/cmdb/ssh/config/` | GET | SSH配置列表 |
| `/cmdb/ssh/config/add/` | GET/POST | 添加SSH配置 |
| `/cmdb/ssh/config/<id>/edit/` | GET/POST | 编辑SSH配置 |
| `/cmdb/ssh/config/import/` | GET/POST | 批量导入SSH配置 |

### 用户管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| `/cmdb/settings/users/` | GET | 用户列表 |
| `/cmdb/settings/users/add/` | GET/POST | 添加用户 |
| `/cmdb/settings/users/<id>/edit/` | GET/POST | 编辑用户 |
| `/cmdb/settings/users/<id>/delete/` | GET | 删除用户 |

## ❓ 常见问题

### Q: 采集失败怎么办？
1. 检查SSH配置是否正确
2. 确认目标服务器SSH端口是否开放
3. 检查用户名密码是否正确
4. 查看Docker日志：`docker logs cmdb-app`

### Q: 如何通过跳板机采集？
1. 在SSH配置中填写跳板机信息
2. 跳板机需能免密登录目标服务器
3. 或者在跳板机上配置SSH跳板

### Q: Cron表达式怎么写？
- `0 2 * * *` - 每天凌晨2点
- `*/30 * * * *` - 每30分钟
- `0 */6 * * *` - 每6小时
- `0 9 * * 1-5` - 工作日上午9点

### Q: 超级管理员有什么权限？
超级管理员自动拥有所有模块的访问权限，无需单独配置权限。

### Q: 数据库连接失败怎么办？
1. 检查docker-compose.yml中的数据库配置
2. 确认数据库容器是否正常运行：`docker ps`
3. 查看数据库日志：`docker logs cmdb-db`

## 📝 维护指南

### 备份数据库

通过系统界面备份：
1. 进入 **数据备份** 页面
2. 点击 **立即备份**

手动备份：
```bash
docker exec cmdb-db mysqldump -u cmdb -pcmdb123 cmdb > backup.sql
```

### 恢复数据库

通过系统界面恢复：
1. 进入 **数据备份** 页面
2. 找到备份记录，点击 **恢复**

手动恢复：
```bash
docker exec -i cmdb-db mysql -u cmdb -pcmdb123 cmdb < backup.sql
```

### 更新代码

```bash
git pull
docker-compose up -d --build
```

### 查看日志

```bash
# 查看应用日志
docker logs -f cmdb-app

# 查看数据库日志
docker logs -f cmdb-db
```

### 重启服务

```bash
docker-compose restart
```

### 停止服务

```bash
docker-compose down
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：dev@example.com

---

**版本**: 1.0.0  
**最后更新**: 2026年5月
