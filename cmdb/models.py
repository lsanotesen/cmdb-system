from django.db import models
from django.contrib.auth.models import User
import json
import ast

ASSET_TYPE = [
    ('1', '物理机'),
    ('2', '虚拟机'),
    ('3', '容器'),
    ('4', '网络设备'),
    ('5', '安全设备'),
    ('6', '其他'),
]

ASSET_STATUS = [
    ('1', '使用中'),
    ('2', '未使用'),
    ('3', '故障'),
    ('4', '其他'),
]

SYSTEM_TYPE = [
    ('linux', 'Linux'),
    ('windows', 'Windows'),
    ('mac', 'MacOS'),
]

COLLECT_STATUS = [
    ('success', '成功'),
    ('failed', '失败'),
    ('partial', '部分成功'),
]


class Idc(models.Model):
    ids = models.CharField('机房标识', max_length=255, unique=True)
    name = models.CharField('机房名称', max_length=100, unique=True)
    address = models.CharField('机房地址', max_length=100, blank=True)
    tel = models.CharField('联系电话', max_length=30, blank=True)
    contact = models.CharField('客户经理', max_length=30, blank=True)
    contact_phone = models.CharField('移动电话', max_length=30, blank=True)
    jigui = models.CharField('机柜信息', max_length=30, blank=True)
    ip_range = models.CharField('IP范围', max_length=30, blank=True)
    bandwidth = models.CharField('带宽', max_length=30, blank=True)
    area = models.CharField('区域', max_length=100, blank=True)
    operator = models.CharField('运营商', max_length=100, blank=True)
    memo = models.TextField('备注', max_length=200, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = '机房'


class Host(models.Model):
    hostname = models.CharField(max_length=50, verbose_name='主机名', unique=True)
    asset_no = models.CharField('资产编号', max_length=50, blank=True)
    cabinet_position = models.CharField('所在机柜位置', max_length=100, blank=True)
    department = models.CharField('所属部门/团队', max_length=100, blank=True)
    asset_type = models.CharField('设备类型', choices=ASSET_TYPE, max_length=30, null=True, blank=True)
    ip = models.GenericIPAddressField('IP地址', max_length=15)
    contact_person = models.CharField('联系人/责任人', max_length=50, blank=True)
    device_model = models.CharField('设备品牌型号', max_length=100, blank=True)
    cpu_model = models.CharField('CPU型号', max_length=200, blank=True)
    cpu_num = models.CharField('CPU数量', max_length=100, blank=True)
    cpu_cores = models.CharField('CPU核数', max_length=100, blank=True)
    gpu_model = models.CharField('GPU型号', max_length=200, blank=True)
    gpu_num = models.CharField('GPU内存', max_length=100, blank=True)
    power_rating = models.CharField('额定功率(W)', max_length=30, blank=True)
    memory = models.CharField('内存大小', max_length=30, blank=True)
    disk = models.CharField('硬盘信息', max_length=255, blank=True)
    os = models.CharField('操作系统', max_length=100, blank=True)
    sn = models.CharField('序列号', max_length=60, blank=True)
    bm_ip = models.GenericIPAddressField('带外管理IP', max_length=15, null=True, blank=True)
    up_time = models.CharField('上架时间', max_length=50, blank=True)
    status = models.CharField('设备状态', choices=ASSET_STATUS, max_length=30, null=True, blank=True)
    memo = models.TextField('备注信息', max_length=200, blank=True)
    idc = models.ForeignKey(Idc, verbose_name='所在机房', on_delete=models.SET_NULL, null=True, blank=True)
    ssh_config = models.ForeignKey('SSHConfig', verbose_name='目标服务器', on_delete=models.SET_NULL, null=True, blank=True, related_name='hosts')
    last_collect_time = models.DateTimeField('上次采集时间', null=True, blank=True)
    is_auto_update = models.BooleanField('自动更新', default=False)
    other_ip = models.CharField('其它IP', max_length=100, blank=True, default='')

    def __str__(self):
        return self.hostname

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = verbose_name


class Cabinet(models.Model):
    idc = models.ForeignKey(Idc, verbose_name='所在机房', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField('机柜', max_length=100)
    desc = models.CharField('描述', max_length=100, blank=True)
    serverList = models.ManyToManyField(Host, blank=True, verbose_name='所在服务器')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机柜'
        verbose_name_plural = verbose_name


class HostGroup(models.Model):
    name = models.CharField('服务器组名', max_length=30, unique=True)
    desc = models.CharField('描述', max_length=100, blank=True)
    serverList = models.ManyToManyField(Host, blank=True, verbose_name='所在服务器')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '动态资产组'
        verbose_name_plural = '动态资产组'


class StaticAssetGroup(models.Model):
    name = models.CharField('静态资产组名', max_length=30, unique=True)
    desc = models.CharField('描述', max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '静态资产组'
        verbose_name_plural = '静态资产组'


class IpSource(models.Model):
    ip = models.GenericIPAddressField('IP地址', max_length=15, null=True, blank=True)
    ip_segment = models.CharField('IP段', max_length=30, null=True, blank=True)
    switch_name = models.CharField('交换机名称', max_length=30, null=True, blank=True)
    switch_port = models.CharField('交换机端口', max_length=30, null=True, blank=True)
    cabinet = models.ForeignKey(Cabinet, verbose_name='所在机柜', on_delete=models.SET_NULL, null=True, blank=True)
    memo = models.TextField('备注', max_length=200, blank=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'IP地址来源'
        verbose_name_plural = verbose_name


class BastionHost(models.Model):
    name = models.CharField('跳板机名称', max_length=100)
    host = models.GenericIPAddressField('IP地址', max_length=15)
    port = models.IntegerField('端口', default=22)
    username = models.CharField('用户名', max_length=100)
    password = models.CharField('密码', max_length=255, blank=True)
    private_key = models.TextField('私钥', blank=True)
    is_enabled = models.BooleanField('启用', default=True)
    memo = models.TextField('备注', max_length=200, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '跳板机'
        verbose_name_plural = verbose_name


class SSHConfig(models.Model):
    name = models.CharField('配置名称', max_length=100, unique=True)
    host = models.GenericIPAddressField('SSH服务器IP', max_length=15)
    port = models.IntegerField('端口', default=22)
    username = models.CharField('用户名', max_length=100)
    password = models.CharField('密码', max_length=255, blank=True)
    private_key = models.TextField('私钥内容', blank=True)
    collect_asset_types = models.CharField('采集资产类型', max_length=50, default='1,2,3', help_text='逗号分隔的类型ID: 1=物理机, 2=虚拟机, 3=容器, 6=其他')
    is_enabled = models.BooleanField('启用状态', default=True)
    memo = models.TextField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    def get_system_type_display(self):
        return 'Linux' if self.system_type == 'linux' else 'Windows' if self.system_type == 'windows' else 'MacOS'

    class Meta:
        verbose_name = '目标服务器'
        verbose_name_plural = verbose_name


class CollectTask(models.Model):
    name = models.CharField('任务名称', max_length=100)
    bastion = models.ForeignKey(BastionHost, verbose_name='跳板机', on_delete=models.SET_NULL, null=True, blank=True, help_text='留空则直连目标服务器')
    target_hosts = models.TextField('目标主机', help_text='IP范围或逗号分隔的IP列表，如: 192.168.1.1-254 或 192.168.1.2')
    target_group = models.ForeignKey(HostGroup, verbose_name='目标资产组', on_delete=models.SET_NULL, null=True, blank=True, help_text='选择资产组后，将采集该组内的所有主机')
    target_port = models.IntegerField('目标SSH端口', default=22)
    target_username = models.CharField('目标用户名', max_length=100, default='root')
    target_password = models.CharField('目标密码', max_length=255, blank=True)
    target_private_key = models.TextField('目标私钥', blank=True)
    collect_online_only = models.BooleanField('仅采集在线主机', default=True)
    jump_via_bastion = models.BooleanField('通过跳板机免密跳转', default=False, help_text='勾选后通过跳板机跳转时使用SSH密钥免密登录（跳板机需配置密钥交换）；不勾选则读取目标服务器的密码进行连接')
    is_auto_collect = models.BooleanField('启用自动采集', default=False)
    cron_expression = models.CharField('定时表达式', max_length=100, blank=True, help_text='格式: 分 时 日 月 周, 如: 0 2 * * * 表示每天凌晨2点')
    is_enabled = models.BooleanField('启用', default=True)
    last_collect_time = models.DateTimeField('上次采集时间', null=True, blank=True)
    last_collect_status = models.CharField('上次采集状态', max_length=20, choices=COLLECT_STATUS, blank=True)
    memo = models.TextField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    update_hostname = models.BooleanField('更新主机名', default=True)
    update_os = models.BooleanField('更新操作系统', default=True)
    update_cpu = models.BooleanField('更新CPU信息', default=True)
    update_memory = models.BooleanField('更新内存', default=True)
    update_disk = models.BooleanField('更新硬盘', default=False)
    update_gpu = models.BooleanField('更新GPU信息', default=True)
    update_device_info = models.BooleanField('更新设备信息', default=True)
    update_sn = models.BooleanField('更新序列号', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '采集任务'
        verbose_name_plural = verbose_name


class CollectHistory(models.Model):
    task = models.ForeignKey(CollectTask, verbose_name='采集任务', on_delete=models.SET_NULL, null=True, blank=True)
    host_ip = models.GenericIPAddressField('主机IP', max_length=15)
    hostname = models.CharField('主机名', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=COLLECT_STATUS)
    cpu_info = models.CharField('CPU信息', max_length=200, blank=True)
    memory_info = models.CharField('内存信息', max_length=100, blank=True)
    disk_info = models.TextField('硬盘信息', blank=True)
    gpu_info = models.CharField('GPU信息', max_length=200, blank=True)
    os_info = models.CharField('操作系统', max_length=100, blank=True)
    sn_info = models.CharField('序列号', max_length=100, blank=True)
    error_message = models.TextField('错误信息', blank=True)
    collect_time = models.DateTimeField('采集时间', auto_now_add=True)

    def __str__(self):
        return f"{self.host_ip} - {self.status}"

    class Meta:
        verbose_name = '采集历史'
        verbose_name_plural = verbose_name
        ordering = ['-collect_time']


class BatchCommand(models.Model):
    name = models.CharField('任务名称', max_length=100)
    bastion = models.ForeignKey(BastionHost, verbose_name='跳板机', on_delete=models.SET_NULL, null=True, blank=True, help_text='留空则直连目标服务器')
    target_hosts = models.TextField('目标主机', help_text='IP范围或逗号分隔的IP列表，如: 192.168.1.1-254 或 192.168.1.2')
    target_group = models.ForeignKey(HostGroup, verbose_name='目标资产组', on_delete=models.SET_NULL, null=True, blank=True, help_text='选择资产组后，将在该组内的所有主机上执行命令')
    target_port = models.IntegerField('目标SSH端口', default=22)
    target_username = models.CharField('目标用户名', max_length=100, default='root')
    target_password = models.CharField('目标密码', max_length=255, blank=True)
    target_private_key = models.TextField('目标私钥', blank=True)
    command = models.TextField('命令内容', help_text='要执行的命令，多条命令请用分号分隔')
    run_as_root = models.BooleanField('以root权限执行', default=True)
    jump_via_bastion = models.BooleanField('通过跳板机免密跳转', default=False, help_text='勾选后通过跳板机跳转时使用SSH密钥免密登录（跳板机需配置密钥交换）；不勾选则读取目标服务器的密码进行连接')
    is_enabled = models.BooleanField('启用', default=True)
    last_run_time = models.DateTimeField('上次运行时间', null=True, blank=True)
    last_run_status = models.CharField('上次运行状态', max_length=20, choices=COLLECT_STATUS, blank=True)
    memo = models.TextField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '批量执行命令'
        verbose_name_plural = verbose_name


class BatchCommandHistory(models.Model):
    command = models.ForeignKey(BatchCommand, verbose_name='命令任务', on_delete=models.SET_NULL, null=True, blank=True)
    host_ip = models.GenericIPAddressField('主机IP', max_length=15)
    hostname = models.CharField('主机名', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=COLLECT_STATUS)
    command_output = models.TextField('命令输出', blank=True)
    error_message = models.TextField('错误信息', blank=True)
    run_time = models.DateTimeField('运行时间', auto_now_add=True)

    def __str__(self):
        return f"{self.host_ip} - {self.status}"

    class Meta:
        verbose_name = '命令执行历史'
        verbose_name_plural = verbose_name
        ordering = ['-run_time']


class StaticAsset(models.Model):
    """静态资产模型"""
    serial_number = models.CharField('序号', max_length=50, blank=True)
    asset_no = models.CharField('服务器资产编号', max_length=100, blank=True)
    cabinet = models.CharField('机柜', max_length=100, blank=True)
    start_u = models.CharField('开始U数', max_length=10, blank=True)
    end_u = models.CharField('结束U数', max_length=10, blank=True)
    department = models.CharField('使用部门/团队（负责人）', max_length=100, blank=True)
    server_type = models.CharField('服务器类型', max_length=100, blank=True)
    ip = models.GenericIPAddressField('IP地址', max_length=15, blank=True, null=True)
    contact_person = models.CharField('联系人/责任人/使用人', max_length=100, blank=True)
    device_model = models.CharField('服务器品牌型号', max_length=100, blank=True)
    server_model = models.CharField('服务器机型（CPU/GPU卡型数量）', max_length=200, blank=True)
    power_rating = models.CharField('服务器额定功率', max_length=50, blank=True)
    memo = models.TextField('备注', max_length=200, blank=True)
    status = models.CharField('状态', max_length=50, blank=True)
    asset_group = models.ForeignKey('StaticAssetGroup', verbose_name='所属静态资产组', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.asset_no or self.ip or f'静态资产{self.id}'

    class Meta:
        verbose_name = '静态资产'
        verbose_name_plural = '静态资产'


class Module(models.Model):
    """系统模块模型"""
    name = models.CharField('模块名称', max_length=100)
    code = models.CharField('模块代码', max_length=50, unique=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '系统模块'
        verbose_name_plural = '系统模块'
        ordering = ['order']


class SparePartType(models.Model):
    """备件类型模型（支持自定义）"""
    name = models.CharField('类型名称', max_length=100)
    code = models.CharField('类型代码', max_length=50, unique=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '备件类型'
        verbose_name_plural = '备件类型管理'
        ordering = ['order']


class SparePart(models.Model):
    """备件模型"""
    STATUS_CHOICES = [
        ('in_stock', '库存中'),
        ('installed', '已安装'),
        ('scrapped', '已报废'),
        ('maintenance', '维修中'),
    ]
    asset_code = models.CharField('备件资产编号', max_length=100, blank=True, null=True, help_text='如 HD-2025-001，可选')
    name = models.CharField('备件名称', max_length=100)
    brand = models.CharField('品牌', max_length=100, blank=True)
    model = models.CharField('型号', max_length=100, blank=True)
    size = models.CharField('大小/规格', max_length=100, blank=True)
    serial_number = models.CharField('序列号', max_length=100, blank=True)
    location = models.CharField('存放位置', max_length=200, blank=True)
    purchase_date = models.DateField('购买日期', blank=True, null=True)
    type = models.ForeignKey('SparePartType', verbose_name='备件类型', on_delete=models.SET_NULL, null=True, blank=True)
    images = models.TextField('图片路径JSON', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='in_stock')
    is_installed = models.BooleanField('是否已安装', default=False)
    installed_host_id = models.IntegerField('安装主机ID', blank=True, null=True)
    installed_slot = models.CharField('安装槽位', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name or self.asset_code or f'备件{self.id}'

    class Meta:
        verbose_name = '备件'
        verbose_name_plural = '备件管理'

    def get_images_list(self):
        """获取图片路径列表"""
        if self.images:
            try:
                return json.loads(self.images)
            except:
                return []


class AssetRelation(models.Model):
    """资产关系模型 - 主资产与子资产的关系"""
    parent_asset = models.ForeignKey('Host', verbose_name='主资产（服务器）', on_delete=models.CASCADE, related_name='child_relations')
    child_asset = models.ForeignKey('Host', verbose_name='子资产（组件）', on_delete=models.CASCADE, related_name='parent_relations')
    slot = models.CharField('槽位', max_length=100, blank=True, help_text='如 PCIe Slot 1, DIMM A1, Disk Bay 2')
    is_removable = models.BooleanField('是否可拆卸', default=True)
    is_active = models.BooleanField('是否有效', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f'{self.parent_asset} -> {self.child_asset} ({self.slot})'

    class Meta:
        verbose_name = '资产关系'
        verbose_name_plural = '资产关系管理'
        unique_together = [('parent_asset', 'slot')]


class InstallHistory(models.Model):
    """安装历史模型"""
    OPERATION_TYPES = [
        ('install', '安装'),
        ('uninstall', '拆卸'),
        ('replacement', '更换'),
        ('expansion', '扩容'),
        ('maintenance', '维护'),
    ]
    asset_relation = models.ForeignKey('AssetRelation', verbose_name='资产关系', on_delete=models.CASCADE, related_name='install_histories')
    install_time = models.DateTimeField('安装时间')
    uninstall_time = models.DateTimeField('拆卸时间', blank=True, null=True)
    operator = models.ForeignKey(User, verbose_name='操作人', on_delete=models.SET_NULL, null=True, blank=True)
    operation_type = models.CharField('操作类型', max_length=20, choices=OPERATION_TYPES)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.operation_type} - {self.asset_relation}'

    class Meta:
        verbose_name = '安装历史'
        verbose_name_plural = '安装历史管理'


class LifecycleEvent(models.Model):
    """生命周期事件模型"""
    EVENT_TYPES = [
        ('purchase', '采购'),
        ('deploy', '上架'),
        ('maintenance', '维护'),
        ('repair', '维修'),
        ('uninstall', '下架'),
        ('reinstall', '重新上架'),
        ('scrap', '报废'),
    ]
    asset = models.ForeignKey('Host', verbose_name='资产', on_delete=models.CASCADE, related_name='lifecycle_events')
    event_type = models.CharField('事件类型', max_length=20, choices=EVENT_TYPES)
    event_time = models.DateTimeField('事件时间')
    operator = models.ForeignKey(User, verbose_name='操作人', on_delete=models.SET_NULL, null=True, blank=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f'{self.asset} - {self.get_event_type_display()}'

    class Meta:
        verbose_name = '生命周期事件'
        verbose_name_plural = '生命周期管理'


class Role(models.Model):
    """角色模型"""
    name = models.CharField('角色名称', max_length=100, unique=True)
    description = models.TextField('角色描述', blank=True)
    permissions = models.TextField('权限JSON', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'

    def get_permissions_list(self):
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except json.JSONDecodeError:
                # 兼容旧数据格式（Python列表字符串）
                try:
                    return ast.literal_eval(self.permissions)
                except (ValueError, SyntaxError):
                    return []
        return []


class UserProfile(models.Model):
    """用户扩展信息模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    real_name = models.CharField('真实姓名', max_length=100, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='userprofiles')
    permissions = models.TextField('个人权限JSON', blank=True)
    phone = models.CharField('电话', max_length=20, blank=True)
    department = models.CharField('部门', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.real_name or self.user.username

    class Meta:
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'

    def get_permissions_list(self):
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except json.JSONDecodeError:
                # 兼容旧数据格式（Python列表字符串）
                try:
                    return ast.literal_eval(self.permissions)
                except (ValueError, SyntaxError):
                    return []
        return []

    def has_permission(self, permission_code):
        if self.permissions:
            permissions_list = self.get_permissions_list()
            # 如果用户有自定义权限，只使用自定义权限，不回退到角色权限
            return permission_code in permissions_list

        # 如果没有自定义权限，使用角色权限
        if self.role and self.role.permissions:
            role_permissions = self.role.get_permissions_list()
            if permission_code in role_permissions:
                return True

        return False


class BackupRecord(models.Model):
    BACKUP_TYPE = [
        ('full', '全量备份'),
        ('incremental', '增量备份'),
    ]
    
    BACKUP_STATUS = [
        ('success', '成功'),
        ('failed', '失败'),
        ('running', '运行中'),
    ]
    
    backup_type = models.CharField('备份类型', max_length=20, choices=BACKUP_TYPE)
    backup_name = models.CharField('备份名称', max_length=255)
    backup_path = models.CharField('备份路径', max_length=500, blank=True)
    file_size = models.CharField('文件大小', max_length=50, blank=True)
    status = models.CharField('备份状态', max_length=20, choices=BACKUP_STATUS)
    backup_time = models.DateTimeField('备份时间', auto_now_add=True)
    error_message = models.TextField('错误信息', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    
    def __str__(self):
        return f"{self.backup_name} - {self.get_backup_type_display()}"
    
    class Meta:
        verbose_name = '备份记录'
        verbose_name_plural = '备份记录'
        ordering = ['-backup_time']

class OperationLog(models.Model):
    ACTION_CHOICES = [
        ('add', '添加'),
        ('edit', '更新'),
        ('delete', '删除'),
        ('import', '导入'),
        ('export', '导出'),
        ('collect', '采集'),
        ('backup', '备份'),
        ('restore', '恢复'),
        ('login', '登录'),
        ('logout', '登出'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    target = models.CharField('操作对象', max_length=255, blank=True)
    description = models.TextField('操作描述', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.target}"
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
