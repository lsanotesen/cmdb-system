#!/usr/bin/env python3
"""
数据迁移脚本：为已退库记录填充冗余字段
"""
import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmdb_project.settings')

import django
django.setup()

from cmdb.models import AssetRelation

def fill_redundant_fields():
    """为已退库记录填充冗余字段"""
    # 获取所有已退库的记录
    returned_relations = AssetRelation.objects.filter(is_returned=True)
    
    count = 0
    for relation in returned_relations:
        updated = False
        
        # 填充主资产信息
        if relation.parent_asset and not relation.parent_asset_no:
            relation.parent_asset_no = relation.parent_asset.asset_no or ''
            relation.parent_asset_name = relation.parent_asset.hostname or relation.parent_asset.memo or ''
            updated = True
        
        # 填充子资产信息
        if relation.child_asset:
            if not relation.child_asset_no:
                relation.child_asset_no = relation.child_asset.asset_no or ''
                updated = True
            if not relation.child_asset_name:
                relation.child_asset_name = relation.child_asset.memo or relation.child_asset.hostname or ''
                updated = True
            if not relation.child_asset_model:
                relation.child_asset_model = relation.child_asset.device_model or ''
                updated = True
            if not relation.child_asset_sn:
                relation.child_asset_sn = relation.child_asset.sn or ''
                updated = True
        
        if updated:
            relation.save()
            count += 1
            print(f"更新记录 {relation.id}")
    
    print(f"\n共更新 {count} 条记录")

if __name__ == '__main__':
    fill_redundant_fields()