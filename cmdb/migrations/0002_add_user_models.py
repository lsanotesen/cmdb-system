from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='模块名称')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='模块代码')),
                ('order', models.IntegerField(default=0, verbose_name='排序')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
            ],
            options={
                'verbose_name': '系统模块',
                'verbose_name_plural': '系统模块',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='角色名称')),
                ('description', models.TextField(blank=True, verbose_name='角色描述')),
                ('permissions', models.TextField(blank=True, verbose_name='权限JSON')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '角色',
                'verbose_name_plural': '角色',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_name', models.CharField(blank=True, max_length=100, verbose_name='真实姓名')),
                ('permissions', models.TextField(blank=True, verbose_name='个人权限JSON')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='电话')),
                ('department', models.CharField(blank=True, max_length=100, verbose_name='部门')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userprofiles', to='cmdb.role', verbose_name='角色')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to='auth.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户扩展信息',
                'verbose_name_plural': '用户扩展信息',
            },
        ),
    ]
