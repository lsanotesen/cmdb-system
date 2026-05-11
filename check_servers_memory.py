#!/usr/bin/env python3
import paramiko
import os

def check_real_memory(ip, port=22):
    try:
        username = os.environ.get('SSH_USER', 'root')
        password = os.environ.get('SSH_PASSWORD', 'Root@123')

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"\n{'='*70}")
        print(f"检查 {ip} 的真实物理内存")
        print(f"{'='*70}")

        client.connect(ip, port=port, username=username, password=password, timeout=10)

        # 方法1: free -m
        print("\n[方法1] free -m 输出:")
        stdin, stdout, stderr = client.exec_command("free -m")
        output = stdout.read().decode('utf-8')
        print(output)

        # 方法2: /proc/meminfo
        print("\n[方法2] /proc/meminfo MemTotal:")
        stdin, stdout, stderr = client.exec_command("awk '/^MemTotal/{print $2}' /proc/meminfo")
        mem_total_kb = stdout.read().decode('utf-8').strip()
        if mem_total_kb:
            mem_mb = int(mem_total_kb) // 1024
            mem_gb = mem_mb / 1024
            print(f"  MemTotal: {mem_total_kb} KB = {mem_mb} MB = {mem_gb:.2f} GB")

        # 方法3: dmidecode
        print("\n[方法3] dmidecode 物理内存信息:")
        try:
            stdin, stdout, stderr = client.exec_command("dmidecode -t 17 2>/dev/null | grep -E 'Size:|Speed:|Type:' | head -30")
            output = stdout.read().decode('utf-8')
            if output.strip():
                print(output)
            else:
                print("  无法获取 dmidecode 信息")
        except:
            print("  dmidecode 执行失败")

        # 方法4: lsmem
        print("\n[方法4] lsmem:")
        try:
            stdin, stdout, stderr = client.exec_command("lsmem 2>/dev/null")
            output = stdout.read().decode('utf-8')
            if output.strip():
                print(output)
            else:
                print("  lsmem 不可用")
        except:
            print("  lsmem 执行失败")

        client.close()
        return True
    except Exception as e:
        print(f"  连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    ips = ['192.168.12.1', '192.168.12.162', '192.168.12.163']

    for ip in ips:
        check_real_memory(ip)
