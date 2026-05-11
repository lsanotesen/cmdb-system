# 资产管理系统

基于 Django + MariaDB 的资产管理平台，支持主机管理、SSH配置管理、硬件信息自动采集、权限管理、机柜布局图等功能。

## 功能特性

### 1. 资产管理
- **动态资产管理**
  - 主机列表、添加、编辑、删除
  - 支持 Excel 批量导入/导出
  - 主机详情查看，包括：资产编号、机柜位置、所属部门、设备类型、IP地址、联系人、设备品牌型号、CPU、GPU、内存、硬盘、操作系统、序列号、带外管理IP、上架时间、设备状态、备注等
- **静态资产管理**
  - 静态资产列表、添加、编辑、删除
  - 支持批量导入/导出
  - 资产分组管理
- **动态资产组**
  - 资产组管理（添加、编辑、删除）
  - 支持按IP范围、标签等条件分组
- **目标服务器管理**
  - 目标服务器列表、添加、编辑、删除
  - 支持批量导入

### 2. SSH配置管理
- 批量导入SSH配置（支持Excel）
- 支持直连模式和跳板机模式
- 批量删除功能

### 3. 硬件信息采集
- 通过SSH远程连接服务器自动采集硬件信息
- 支持跳板机跳转连接
- 采集内容：主机名、操作系统、CPU型号/数量、内存、硬盘、GPU、序列号、设备型号
- 支持定时采集和立即采集
- 可配置只采集在线服务器
- 实时采集进度追踪

### 4. 机房管理
- 机房增删改查
- 机柜管理
- 主机组管理
- 机柜布局图可视化

### 5. 机柜布局图
- 可视化机柜布局展示
- 支持导出 Excel（带样式和布局图图片）
- 支持导出 HTML（保留完整样式）
- 支持导出 PNG 图片

### 6. IP来源管理
- IP地址段管理
- 交换机端口关联

### 7. 权限管理系统
- **用户管理**
  - 添加、编辑、删除用户
  - 用户状态管理
  - 修改密码
- **角色管理**
  - 创建角色、分配权限
  - 角色权限配置
- **权限管理**
  - 细粒度权限控制（查看、添加、编辑、删除、下载）
  - 支持自定义权限和角色权限
  - 超级管理员自动拥有所有权限

### 8. 数据备份
- 数据库备份
- 备份文件管理
- **数据恢复**：支持上传SQL文件恢复，支持从备份列表直接恢复，自动处理外键约束
- 备份历史记录
- 自动清理过期备份（可配置保留数量）

### 9. 批量命令执行
- 支持批量执行命令
- 命令执行进度追踪
- 执行结果查看

### 10. 跳板机管理
- 跳板机配置管理
- 支持多跳板机配置

## 系统架构

```
┌─────────────────┐     ┌─────────────────┐
│   Web UI        │     │   SSH Config    │
│   (Django)      │────▶│   Management    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│              MySQL/MariaDB              │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     Hardware Collection Engine          │
│     (Paramiko SSH + ThreadPool)         │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Target Servers via Bastion/Jump Host  │
└─────────────────────────────────────────┘
```

## 快速开始

### 环境要求
- Docker & Docker Compose
- 或 Python 3.10+ with Django 4.2

### 使用 Docker 部署

#### 1. 克隆项目

```bash
git clone https://github.com/lsanotesen/cmdb-system.git
cd cmdb-system
```

#### 2. 启动服务

```bash
docker-compose up -d --build
```

**说明**：
- 首次启动需要使用 `--build` 参数构建镜像
- 数据库迁移和权限初始化会**自动执行**，无需手动操作
- 数据库数据持久化存储在 `/data01/mysql_data` 目录
- **重要**：请根据实际部署环境修改 `docker-compose.yml` 中的挂载目录路径（如 `/data01/`），确保该目录存在且有写入权限

#### 3. 管理员账号

**默认管理员账号**（首次部署后**自动创建**）：
- 用户名：`admin`
- 密码：`Admin1234`

如需创建其他管理员账号，可执行：

```bash
docker-compose exec cmdb python3 manage.py createsuperuser
```

#### 4. 访问系统

```
前台: http://localhost:8001/cmdb/
管理后台: http://localhost:8001/admin/
```

#### 5. 数据持久化说明

数据库数据存储在主机的 `/data01/mysql_data` 目录中，即使执行 `docker-compose down -v` 也不会丢失数据。

### 部署说明

启动脚本会自动执行以下操作：
1. 等待数据库服务完全就绪
2. 执行数据库迁移（`migrate`）
3. 初始化权限数据（`init_permissions.py`）
4. 启动 Django 应用

这样可以确保服务启动顺序正确，避免因数据库未就绪导致的连接失败问题。

### 配置文件

环境变量配置（docker-compose.yml）:
```yaml
environment:
  - DB_HOST=db
  - DB_PORT=3306
  - DB_USER=cmdb
  - DB_PASSWORD=cmdb123
  - DB_NAME=cmdb
```

**数据存储配置**：
```yaml
volumes:
  - /data01/mysql_data:/var/lib/mysql  # 数据库数据持久化到主机目录
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

## 使用说明

### 权限管理

#### 创建角色

1. 进入 **系统设置 > 角色管理**
2. 点击 **添加角色**
3. 填写角色名称（如：管理员、运维人员、查看者）
4. 选择该角色拥有的权限（按模块分类）
5. 保存

#### 添加用户

1. 进入 **系统设置 > 用户管理**
2. 点击 **添加用户**
3. 填写用户信息：
   - 用户名
   - 密码
   - 邮箱
   - 所属角色（可选）
   - 自定义权限（可选，会覆盖角色权限）
4. 保存

#### 修改密码

1. 点击右上角用户名
2. 选择 **修改密码**
3. 输入旧密码和新密码
4. 保存

**注意**：超级管理员（is_superuser=True）自动拥有所有模块的访问权限。

### 添加SSH配置

1. 进入 **SSH配置** 页面
2. 点击 **添加SSH配置**
3. 填写配置信息：
   - **配置名称**：如 "测试服务器-192.168.1.1"
   - **目标服务器IP**：要采集的服务器IP
   - **端口**：SSH端口，默认22
   - **用户名/密码**：服务器登录凭据
   - **跳板机信息**（可选）：
     - 如果需要通过跳板机连接，填写跳板机IP、端口、用户名、密码
     - 留空则直连目标服务器

4. 设置采集资产类型和启用状态
5. 保存

### 批量导入SSH配置

1. 进入 **SSH配置** 页面
2. 点击 **批量导入**
3. 下载模板，填写Excel：
   | 配置名称 | 目标服务器IP | 端口 | 用户名 | 密码 | 采集资产类型 | 启用状态 | 备注 |
   |---------|------------|------|-------|------|------------|---------|-----|
   | 服务器-01 | 192.168.1.1 | 22 | root | password | 物理机 | 是 | 备注 |
4. 上传填好的Excel文件
5. 点击开始导入

### 创建采集任务

1. 进入 **采集任务** 页面
2. 点击 **新建任务**
3. 填写任务信息：
   - **任务名称**：如 "每日采集任务"
   - **SSH配置**：选择使用的SSH配置，留空则使用所有启用的配置
   - **目标主机**：留空则采集所有配置了SSH的主机，或填写IP范围如 `192.168.1.1-192.168.1.200`
   - **采集选项**：
     - ☑️ 采集在线服务器（只采集在线的）
     - ☑️ 启用定时采集（设置cron表达式）
   - **Cron表达式**：
     - `0 2 * * *` 每天凌晨2点
     - `*/30 * * * *` 每30分钟
     - `0 */6 * * *` 每6小时
4. 保存

### 立即采集

1. 进入 **采集任务** 页面
2. 找到目标任务，点击 **⚡ 立即采集**
3. 系统将跳转到进度页面，实时显示采集进度
4. 采集完成后自动跳转到采集结果页面

### 机柜布局图

1. 进入 **机柜管理** 页面
2. 点击 **布局图** 按钮查看机柜布局
3. 导出功能：
   - **导出Excel**：导出表格数据 + 布局图图片（两页）
   - **导出HTML**：导出保留完整样式的HTML文件
   - **导出图片**：导出PNG图片

### 数据备份

1. 进入 **数据备份** 页面
2. 点击 **立即备份** 创建新的备份
3. 备份列表显示所有备份记录
4. 可以下载备份文件或恢复数据

## 目录结构

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
├── docker-compose.yml         # Docker编排
├── Dockerfile                # Docker镜像配置
├── requirements.txt          # Python依赖
├── init_permissions.py       # 权限初始化脚本
├── manage.py                 # Django管理脚本
├── hw_collector.py           # 硬件采集脚本
└── README.md                 # 本文档
```

## 数据模型

### Host（主机）
| 字段 | 说明 |
|-----|------|
| asset_num | 资产编号 |
| hostname | 主机名 |
| ip | IP地址 |
| cabinet_position | 机柜位置 |
| department | 所属部门 |
| device_type | 设备类型（1-物理机,2-虚拟机,3-容器,4-网络设备,5-安全设备,6-其他） |
| contact | 联系人 |
| phone | 联系电话 |
| brand_model | 品牌型号 |
| cpu_model | CPU型号 |
| cpu_num | CPU数量 |
| gpu_model | GPU型号 |
| gpu_num | GPU数量 |
| power | 额定功率 |
| memory | 内存 |
| disk | 硬盘 |
| os | 操作系统 |
| sn | 序列号 |
| oob_ip | 带外管理IP |
| shelf_time | 上架时间 |
| status | 设备状态 |
| memo | 备注 |

### StaticAsset（静态资产）
| 字段 | 说明 |
|-----|------|
| asset_no | 资产编号 |
| name | 资产名称 |
| category | 资产类别 |
| model | 型号 |
| brand | 品牌 |
| serial_number | 序列号 |
| purchase_date | 购买日期 |
| price | 价格 |
| status | 状态 |
| location | 位置 |
| department | 所属部门 |
| contact | 联系人 |
| memo | 备注 |

### StaticAssetGroup（静态资产组）
| 字段 | 说明 |
|-----|------|
| name | 组名 |
| description | 描述 |
| options | 配置选项 |

### SSHConfig（SSH配置）
| 字段 | 说明 |
|-----|------|
| name | 配置名称 |
| host | 目标服务器IP |
| port | SSH端口 |
| username | 用户名 |
| password | 密码 |
| private_key | 私钥内容 |
| bastion_host | 跳板机IP（留空直连） |
| bastion_port | 跳板机端口 |
| bastion_username | 跳板机用户名 |
| bastion_password | 跳板机密码 |
| bastion_private_key | 跳板机私钥 |
| is_enabled | 是否启用 |
| collect_asset_types | 采集资产类型 |
| memo | 备注 |

### CollectTask（采集任务）
| 字段 | 说明 |
|-----|------|
| name | 任务名称 |
| ssh_config | 关联的SSH配置 |
| target_hosts | 目标主机（留空采集所有） |
| collect_online_only | 只采集在线 |
| is_auto_collect | 启用定时采集 |
| cron_expression | Cron表达式 |
| is_enabled | 是否启用 |
| last_collect_time | 上次采集时间 |
| last_collect_status | 上次采集状态 |
| memo | 备注 |

### Idc（机房）
| 字段 | 说明 |
|-----|------|
| name | 机房名称 |
| address | 地址 |
| operator | 运营商 |
| contact | 联系人 |
| phone | 联系电话 |
| memo | 备注 |

### Cabinet（机柜）
| 字段 | 说明 |
|-----|------|
| name | 机柜名称 |
| idc | 所属机房 |
| position | 位置 |
| u_count | U位数量 |
| memo | 备注 |

### User（用户）
| 字段 | 说明 |
|-----|------|
| username | 用户名 |
| password | 密码（加密） |
| email | 邮箱 |
| is_active | 是否激活 |
| is_superuser | 是否超级管理员 |

### Role（角色）
| 字段 | 说明 |
|-----|------|
| name | 角色名称 |
| description | 描述 |
| permissions | 权限列表 |

### UserProfile（用户配置）
| 字段 | 说明 |
|-----|------|
| user | 关联用户 |
| role | 关联角色 |
| permissions | 自定义权限 |

### BackupRecord（备份记录）
| 字段 | 说明 |
|-----|------|
| backup_time | 备份时间 |
| backup_file | 备份文件 |
| file_size | 文件大小 |
| operator | 操作人 |

## API接口

### 资产管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/assets/ | GET | 资产列表 |
| /cmdb/assets/add/ | GET/POST | 添加资产 |
| /cmdb/assets/<id>/edit/ | GET/POST | 编辑资产 |
| /cmdb/assets/<id>/delete/ | GET | 删除资产 |
| /cmdb/assets/import/ | GET/POST | Excel导入 |
| /cmdb/assets/export/excel/ | GET | Excel导出 |

### 静态资产
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/static-assets/ | GET | 静态资产列表 |
| /cmdb/static-assets/add/ | GET/POST | 添加静态资产 |
| /cmdb/static-assets/<id>/edit/ | GET/POST | 编辑静态资产 |
| /cmdb/static-assets/<id>/delete/ | GET | 删除静态资产 |
| /cmdb/static-assets/import/ | GET/POST | 批量导入 |

### 静态资产组
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/static-asset-groups/ | GET | 资产组列表 |
| /cmdb/static-asset-groups/add/ | GET/POST | 添加资产组 |
| /cmdb/static-asset-groups/<id>/edit/ | GET/POST | 编辑资产组 |
| /cmdb/static-asset-groups/<id>/delete/ | GET | 删除资产组 |

### 目标服务器
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/target-servers/ | GET | 目标服务器列表 |
| /cmdb/target-servers/add/ | GET/POST | 添加目标服务器 |
| /cmdb/target-servers/<id>/edit/ | GET/POST | 编辑目标服务器 |
| /cmdb/target-servers/<id>/delete/ | GET | 删除目标服务器 |
| /cmdb/target-servers/import/ | GET/POST | 批量导入 |

### 机房管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/idc/ | GET | 机房列表 |
| /cmdb/idc/add/ | GET/POST | 添加机房 |
| /cmdb/idc/<id>/edit/ | GET/POST | 编辑机房 |
| /cmdb/idc/<id>/delete/ | GET | 删除机房 |

### 机柜管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/cabinets/ | GET | 机柜列表 |
| /cmdb/cabinets/add/ | GET/POST | 添加机柜 |
| /cmdb/cabinets/<id>/edit/ | GET/POST | 编辑机柜 |
| /cmdb/cabinets/<id>/delete/ | GET | 删除机柜 |
| /cmdb/cabinets/layout/ | GET | 机柜布局图 |

### SSH配置
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/ssh/config/ | GET | SSH配置列表 |
| /cmdb/ssh/config/add/ | GET/POST | 添加SSH配置 |
| /cmdb/ssh/config/<id>/edit/ | GET/POST | 编辑SSH配置 |
| /cmdb/ssh/config/<id>/delete/ | GET | 删除SSH配置 |
| /cmdb/ssh/config/batch/delete/ | POST | 批量删除SSH配置 |
| /cmdb/ssh/config/import/ | GET/POST | 批量导入SSH配置 |
| /cmdb/ssh/config/export/ | GET | 导出SSH配置模板 |

### 采集任务
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/collect/tasks/ | GET | 采集任务列表 |
| /cmdb/collect/tasks/add/ | GET/POST | 创建采集任务 |
| /cmdb/collect/tasks/<id>/immediate/ | GET | 立即采集 |
| /cmdb/collect/tasks/<id>/run/ | GET | 定时执行 |
| /cmdb/collect/history/ | GET | 采集历史 |

### 数据备份
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/backup/ | GET | 备份列表 |
| /cmdb/backup/create/ | POST | 创建备份 |
| /cmdb/backup/restore/<id>/ | POST | 恢复备份 |
| /cmdb/backup/download/<id>/ | GET | 下载备份 |

### 用户管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/settings/users/ | GET | 用户列表 |
| /cmdb/settings/users/add/ | GET/POST | 添加用户 |
| /cmdb/settings/users/<id>/edit/ | GET/POST | 编辑用户 |
| /cmdb/settings/users/<id>/delete/ | GET | 删除用户 |
| /cmdb/settings/users/<id>/permissions/ | GET/POST | 用户权限配置 |
| /cmdb/change-password/ | GET/POST | 修改密码 |

### 角色管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/settings/roles/ | GET | 角色列表 |
| /cmdb/settings/roles/add/ | GET/POST | 添加角色 |
| /cmdb/settings/roles/<id>/edit/ | GET/POST | 编辑角色 |
| /cmdb/settings/roles/<id>/delete/ | GET | 删除角色 |

### 权限管理
| 路径 | 方法 | 说明 |
|-----|------|-----|
| /cmdb/settings/permissions/ | GET | 权限列表 |

## 常见问题

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

### Q: 如何重置管理员密码？
1. 进入系统设置 > 用户管理
2. 找到管理员账号，点击编辑
3. 修改密码并保存

### Q: 数据库连接失败怎么办？
1. 检查docker-compose.yml中的数据库配置
2. 确认数据库容器是否正常运行：`docker ps`
3. 查看数据库日志：`docker logs cmdb-db`

## 维护指南

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

**说明**：数据库迁移会自动执行，无需手动操作。

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

**说明**：重启后数据库迁移和权限初始化会自动执行。

### 停止服务

```bash
docker-compose down
```

### 清理数据

```bash
# 停止并删除容器、网络（数据保留）
docker-compose down

# 重新初始化（数据会保留）
docker-compose up -d --build

# 如果需要完全清理数据（删除主机目录）
rm -rf /data01/mysql_data
docker-compose down
docker-compose up -d --build
docker-compose exec cmdb python3 manage.py createsuperuser
```

**说明**：
- 数据库数据存储在 `/data01/mysql_data`，执行 `docker-compose down -v` 不会删除数据
- 如需完全清理数据，需要手动删除 `/data01/mysql_data` 目录

## 技术栈

- **后端框架**: Django 4.2
- **数据库**: MariaDB 10.11
- **Web服务器**: Gunicorn
- **容器化**: Docker & Docker Compose
- **SSH连接**: Paramiko
- **Excel处理**: openpyxl
- **前端**: Bootstrap 5, jQuery

## License

MIT License
