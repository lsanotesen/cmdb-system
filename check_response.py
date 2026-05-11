#!/usr/bin/env python3
"""
检查采集任务和批量命令执行功能的响应内容
"""
import requests

# 服务器地址
BASE_URL = 'http://localhost:8002/cmdb'

def check_collect_task_response():
    """检查采集任务执行的响应内容"""
    print("=== 检查采集任务执行响应 ===")
    
    # 这里假设已经有一个采集任务，ID为1
    task_id = 1
    
    try:
        response = requests.get(f'{BASE_URL}/collect/task/{task_id}/run/')
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
        # 打印响应的前 500 个字符
        print("\n响应内容前 500 个字符:")
        print(response.text[:500])
        
        # 检查是否包含关键内容
        if '采集任务进度' in response.text:
            print("\n✓ 响应包含 '采集任务进度' 字符串")
        else:
            print("\n✗ 响应不包含 '采集任务进度' 字符串")
            
        if 'collect_task_progress' in response.text:
            print("✓ 响应包含 'collect_task_progress' 字符串")
        else:
            print("✗ 响应不包含 'collect_task_progress' 字符串")
            
    except Exception as e:
        print(f"✗ 执行采集任务异常: {e}")

def check_batch_command_response():
    """检查批量命令执行的响应内容"""
    print("\n=== 检查批量命令执行响应 ===")
    
    # 这里假设已经有一个命令任务，ID为1
    command_id = 1
    
    try:
        response = requests.get(f'{BASE_URL}/batch/command/{command_id}/run/')
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
        # 打印响应的前 500 个字符
        print("\n响应内容前 500 个字符:")
        print(response.text[:500])
        
        # 检查是否包含关键内容
        if '命令执行进度' in response.text:
            print("\n✓ 响应包含 '命令执行进度' 字符串")
        else:
            print("\n✗ 响应不包含 '命令执行进度' 字符串")
            
        if 'batch_command_progress' in response.text:
            print("✓ 响应包含 'batch_command_progress' 字符串")
        else:
            print("✗ 响应不包含 'batch_command_progress' 字符串")
            
    except Exception as e:
        print(f"✗ 执行命令异常: {e}")

if __name__ == '__main__':
    check_collect_task_response()
    check_batch_command_response()
    print("\n=== 检查完成 ===")