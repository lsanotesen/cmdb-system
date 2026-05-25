# Generated manually to add cabinet field to IpSource
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0014_add_is_admin_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipsource',
            name='cabinet',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='cmdb.cabinet', verbose_name='所在机柜'),
        ),
    ]
