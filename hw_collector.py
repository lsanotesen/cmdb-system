#!/usr/bin/env python3
import os
import sys
import json
import paramiko
import concurrent.futures
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
import argparse


@dataclass
class HardwareInfo:
    hostname: str = ''
    ip: str = ''
    os: str = ''
    os_version: str = ''
    cpu_model: str = ''
    cpu_num: int = 0
    cpu_cores: int = 0
    memory_total: str = ''
    memory_bytes: int = 0
    disk_info: str = ''
    disk_num: int = 0
    gpu_model: str = ''
    gpu_num: int = 0
    gpu_memory: str = ''
    sn: str = ''
    vendor: str = ''
    product: str = ''
    bm_ip: str = ''
    power_rating: str = ''
    asset_type: str = ''  # 1: 物理机, 2: 虚拟机, 3: 容器, 4: 网络设备, 5: 安全设备, 6: 其他
    status: str = '1'  # 1: 使用中, 2: 未使用, 3: 故障, 4: 其他
    error: str = ''

    def to_cmdb_dict(self) -> Dict:
        return {
            'hostname': self.hostname,
            'ip': self.ip,
            'os': f"{self.os} {self.os_version}".strip(),
            'cpu_model': self.cpu_model,
            'cpu_num': str(self.cpu_num),
            'memory': self.memory_total,
            'disk': self.disk_info,
            'gpu_model': self.gpu_model,
            'gpu_num': str(self.gpu_num),
            'sn': self.sn,
            'device_model': f"{self.vendor} {self.product}".strip(),
            'bm_ip': self.bm_ip,
            'power_rating': self.power_rating,
            'asset_type': self.asset_type,
            'status': self.status,
        }

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(data: str) -> 'HardwareInfo':
        return HardwareInfo(**json.loads(data))


class SSHClient:
    def __init__(self, host: str, port: int, username: str, password: str, timeout: int = 30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> bool:
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                banner_timeout=self.timeout
            )
            return True
        except Exception as e:
            return False

    def exec_command(self, cmd: str) -> tuple:
        if not self.client:
            return '', f'Not connected'
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd, timeout=self.timeout)
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode('utf-8', errors='ignore').strip()
            stderr_str = stderr.read().decode('utf-8', errors='ignore').strip()
            return stdout_str, stderr_str if exit_code != 0 else ''
        except Exception as e:
            return '', str(e)

    def close(self):
        if self.client:
            self.client.close()


class HardwareCollector:
    def __init__(self, ssh_client: SSHClient):
        self.ssh = ssh_client

    def collect(self, collect_disk: bool = True) -> HardwareInfo:
        info = HardwareInfo()
        info.ip = self.ssh.host

        if not self.ssh.connect():
            info.error = f"SSH连接失败"
            return info

        try:
            info.hostname = self._get_hostname()
            info.os, info.os_version = self._get_os_info()
            info.cpu_model, info.cpu_num, info.cpu_cores = self._get_cpu_info()
            info.memory_total, info.memory_bytes = self._get_memory_info()
            if collect_disk:
                info.disk_info, info.disk_num = self._get_disk_info()
            info.gpu_model, info.gpu_num, info.gpu_memory = self._get_gpu_info()
            info.sn, info.vendor, info.product = self._get_system_info()
            info.power_rating = self._get_power_info()
            info.asset_type = self._detect_asset_type()
            info.bm_ip = self._get_bm_ip()
            info.status = '1'  # 采集成功，设备状态设置为使用中
        except Exception as e:
            info.error = str(e)

        return info

    def _get_hostname(self) -> str:
        output, _ = self.ssh.exec_command('hostname -f 2>/dev/null || hostname')
        return output or ''

    def _get_os_info(self) -> tuple:
        # 尝试从 /etc/os-release 获取（现代 Linux 发行版）
        os_name, _ = self.ssh.exec_command("grep '^NAME=' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '\"'")
        os_version, _ = self.ssh.exec_command("grep '^VERSION=' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '\"'")
        
        # 如果 /etc/os-release 失败，尝试从 /etc/redhat-release 获取（CentOS 6 等旧版本）
        if not os_name:
            redhat_release, _ = self.ssh.exec_command("cat /etc/redhat-release 2>/dev/null")
            if redhat_release:
                # 解析 CentOS 6 的版本信息
                # 例如：CentOS release 6.10 (Final)
                import re
                match = re.match(r'(.+) release (\d+\.\d+)', redhat_release)
                if match:
                    os_name = match.group(1)
                    os_version = match.group(2)
        
        # 如果仍然失败，使用 uname 命令
        if not os_name:
            os_name, _ = self.ssh.exec_command('uname -s')
            os_version, _ = self.ssh.exec_command('uname -r')
        
        return os_name, os_version

    def _get_cpu_info(self) -> tuple:
        cpu_model, _ = self.ssh.exec_command(
            "grep 'model name' /proc/cpuinfo 2>/dev/null | head -1 | cut -d: -f2 | sed 's/^ *//'"
        )
        if not cpu_model:
            cpu_model, _ = self.ssh.exec_command("lscpu | grep 'Model name' | awk -F: '{print $2}' | sed 's/^ *//'")

        # 获取物理CPU数量（插槽数）
        cpu_num_str, _ = self.ssh.exec_command("lscpu | grep -E '座|Socket' | awk '{print $2}' 2>/dev/null || echo 1")
        try:
            cpu_num = int(cpu_num_str.strip())
        except:
            # 备用方法
            cpu_num_str, _ = self.ssh.exec_command("grep 'physical id' /proc/cpuinfo 2>/dev/null | sort -u | wc -l")
            try:
                cpu_num = int(cpu_num_str.strip())
            except:
                cpu_num = 1

        # 获取每个物理CPU的核心数
        cpu_cores_str, _ = self.ssh.exec_command("lscpu | grep -E '每个座的核数|Core\(s\) per socket' | awk -F':' '{print $2}' | xargs 2>/dev/null")
        try:
            cpu_cores = int(cpu_cores_str.strip())
        except:
            # 备用方法
            cpu_cores_str, _ = self.ssh.exec_command("grep 'cpu cores' /proc/cpuinfo 2>/dev/null | head -1 | awk '{print $4}'")
            try:
                cpu_cores = int(cpu_cores_str.strip())
            except:
                cpu_cores = 1

        return cpu_model, cpu_num, cpu_cores

    def _get_memory_info(self) -> tuple:
        # 优先使用 /proc/meminfo 获取内存总量（更准确）
        mem_total, _ = self.ssh.exec_command("grep MemTotal /proc/meminfo | awk '{print $2}'")
        if mem_total and mem_total.strip() and mem_total.strip().isdigit():
            try:
                mem_kb = int(mem_total.strip())
                mem_bytes = mem_kb * 1024
                mem_total_formatted = self._format_bytes(mem_bytes)
                return mem_total_formatted, mem_bytes
            except:
                pass

        # 备用方法: 使用 free -b 命令
        mem_info, _ = self.ssh.exec_command("free -b 2>/dev/null | grep Mem")
        if mem_info and 'Mem:' in mem_info:
            parts = mem_info.split()
            if len(parts) >= 2:
                mem_bytes_str = parts[1]
                try:
                    mem_bytes = int(mem_bytes_str)
                    mem_total_formatted = self._format_bytes(mem_bytes)
                    return mem_total_formatted, mem_bytes
                except:
                    pass

        # 最后尝试 free -h 命令
        mem_total_str, _ = self.ssh.exec_command("free -h 2>/dev/null | grep Mem | awk '{print $2}'")
        if mem_total_str:
            return mem_total_str, 0

        return 'Unknown', 0

    def _format_bytes(self, bytes_val: int) -> str:
        if bytes_val < 1024:
            return f"{bytes_val}B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val // 1024}KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val // (1024 * 1024)}MB"
        elif bytes_val < 1024 * 1024 * 1024 * 1024:
            # 使用整数除法，避免浮点数精度问题
            mem_gb = bytes_val // (1024 * 1024 * 1024)
            # 计算余数，检查是否接近整数
            remainder = (bytes_val % (1024 * 1024 * 1024)) // (1024 * 1024)  # 转换为MB
            if remainder < 100:  # 允许 100MB 的误差
                return f"{mem_gb}GB"
            else:
                # 保留一位小数
                mem_gb_float = bytes_val / (1024 * 1024 * 1024)
                return f"{mem_gb_float:.1f}GB"
        else:
            return f"{bytes_val // (1024 * 1024 * 1024 * 1024)}TB"

    def _get_disk_info(self) -> tuple:
        disk_info, _ = self.ssh.exec_command(
            "lsblk -d -o NAME,SIZE,TYPE -n 2>/dev/null | grep disk || echo 'Unknown'"
        )
        disk_num_str, _ = self.ssh.exec_command(
            "lsblk -d -o NAME -n 2>/dev/null | grep -c disk || echo 1"
        )
        try:
            disk_num = int(disk_num_str)
        except:
            disk_num = 1

        if disk_info:
            lines = disk_info.strip().split('\n')
            formatted = []
            for line in lines[:5]:
                parts = line.split()
                if len(parts) >= 2:
                    formatted.append(f"{parts[0]} {parts[1]}")
            disk_info = ', '.join(formatted)
            if len(lines) > 5:
                disk_info += f' (+{len(lines)-5} more)'

        return disk_info, disk_num

    def _get_gpu_info(self) -> tuple:
        gpu_info, _ = self.ssh.exec_command("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null")
        if not gpu_info:
            gpu_vendor, _ = self.ssh.exec_command("lspci | grep -i vga | head -1")
            if gpu_vendor and 'nvidia' in gpu_vendor.lower():
                return 'NVIDIA GPU', 1, 'Unknown'
            elif gpu_vendor and 'amd' in gpu_vendor.lower():
                return 'AMD GPU', 1, 'Unknown'
            return '', 0, ''

        lines = gpu_info.strip().split('\n')
        gpu_info_list = []

        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                gpu_name = parts[0]
                mem_str = parts[1]
                # 提取内存数值
                import re
                match = re.search(r'([0-9.]+)', mem_str)
                if match:
                    try:
                        value = float(match.group(1))
                        mem_mb = int(value)
                        gpu_info_list.append({'name': gpu_name, 'memory': f"{mem_mb}MB"})
                    except Exception:
                        pass

        if gpu_info_list:
            # 统计不同型号的 GPU 数量和内存
            gpu_model_count = {}
            for gpu in gpu_info_list:
                model_key = f"{gpu['name']}  {gpu['memory']}"
                if model_key not in gpu_model_count:
                    gpu_model_count[model_key] = {'name': gpu['name'], 'memory': gpu['memory'], 'count': 0}
                gpu_model_count[model_key]['count'] += 1
            
            # 生成 GPU 型号字符串（包含内存和数量）
            gpu_model_parts = []
            for model_info in gpu_model_count.values():
                gpu_model_parts.append(f"{model_info['name']}  {model_info['memory']}  x{model_info['count']}")
            
            # 格式化 GPU 型号
            gpu_model = '\n'.join(gpu_model_parts)
            gpu_num = len(gpu_info_list)
            gpu_memory = ', '.join([gpu['memory'] for gpu in gpu_info_list])
            return gpu_model, gpu_num, gpu_memory
        else:
            return '', 0, ''

    def _get_system_info(self) -> tuple:
        sn, _ = self.ssh.exec_command("dmidecode -s system-serial-number 2>/dev/null | head -1")
        if not sn or 'No such' in sn or 'Permission' in sn:
            sn, _ = self.ssh.exec_command("cat /sys/class/dmi/id/product_serial 2>/dev/null")

        vendor, _ = self.ssh.exec_command("dmidecode -s system-manufacturer 2>/dev/null | head -1")
        if not vendor or 'No such' in vendor:
            vendor, _ = self.ssh.exec_command("cat /sys/class/dmi/id/sys_vendor 2>/dev/null")

        product, _ = self.ssh.exec_command("dmidecode -s system-product-name 2>/dev/null | head -1")
        if not product or 'No such' in product:
            product, _ = self.ssh.exec_command("cat /sys/class/dmi/id/product_name 2>/dev/null")

        return sn.strip() if sn else '', vendor.strip() if vendor else '', product.strip() if product else ''

    def _detect_asset_type(self) -> str:
        """检测设备类型：物理机、虚拟机或其他"""
        # 方法1: 检查 system-manufacturer
        vendor, _ = self.ssh.exec_command("dmidecode -s system-manufacturer 2>/dev/null | head -1")
        if not vendor or 'No such' in vendor:
            vendor, _ = self.ssh.exec_command("cat /sys/class/dmi/id/sys_vendor 2>/dev/null")
        vendor_lower = vendor.lower()
        
        if any(vm in vendor_lower for vm in ['vmware', 'virtualbox', 'microsoft', 'qemu', 'xen', 'kvm', 'parallels']):
            return '2'  # 虚拟机
        
        # 方法2: 检查 systemd-detect-virt
        virt_type, _ = self.ssh.exec_command("systemd-detect-virt 2>/dev/null")
        if virt_type and virt_type.strip() != 'none':
            return '2'  # 虚拟机
        
        # 方法3: 检查 /proc/cpuinfo 中的 hypervisor 标识
        hypervisor, _ = self.ssh.exec_command("grep -c hypervisor /proc/cpuinfo 2>/dev/null")
        try:
            if int(hypervisor.strip()) > 0:
                return '2'  # 虚拟机
        except:
            pass
        
        # 方法4: 检查产品名称
        product, _ = self.ssh.exec_command("dmidecode -s system-product-name 2>/dev/null | head -1")
        if not product or 'No such' in product:
            product, _ = self.ssh.exec_command("cat /sys/class/dmi/id/product_name 2>/dev/null")
        product_lower = product.lower()
        if any(vm in product_lower for vm in ['virtual', 'vmware', 'kvm', 'qemu', 'xen']):
            return '2'  # 虚拟机
        
        # 默认为物理机
        return '1'  # 物理机

    def _get_power_info(self) -> str:
        power, _ = self.ssh.exec_command("ipmitool sensor 2>/dev/null | grep -i 'Power' | grep -v 'Power Cap' | head -1")
        if power:
            parts = power.split('|')
            if parts:
                try:
                    return parts[0].strip().split()[0] + 'W'
                except:
                    pass

        power, _ = self.ssh.exec_command("dmidecode -s power-supply-max-input-power 2>/dev/null | head -1")
        if power and 'No such' not in power:
            return f"{power.strip()}W"

        return ''

    def _get_bm_ip(self) -> str:
        # 先加载IPMI相关模块
        self.ssh.exec_command("modprobe ipmi_msghandler 2>/dev/null")
        self.ssh.exec_command("modprobe ipmi_si 2>/dev/null")
        self.ssh.exec_command("modprobe ipmi_devintf 2>/dev/null")
        
        # 然后查询带外IP
        bm_ip, _ = self.ssh.exec_command("ipmitool lan print 2>/dev/null | awk -F':' '/IP Address[[:space:]]+:/ {print $2}' | xargs")
        if bm_ip and bm_ip.strip():
            return bm_ip.strip()
        return ''


def collect_single_server(host: str, port: int, username: str, password: str, collect_disk: bool = True) -> HardwareInfo:
    ssh = SSHClient(host, port, username, password)
    collector = HardwareCollector(ssh)
    return collector.collect(collect_disk=collect_disk)


def collect_multiple_servers(servers: List[Dict], max_workers: int = 10) -> List[HardwareInfo]:
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_server = {
            executor.submit(
                collect_single_server,
                s['host'], s.get('port', 22), s['username'], s['password']
            ): s for s in servers
        }
        for future in concurrent.futures.as_completed(future_to_server):
            results.append(future.result())
    return results


def servers_from_file(file_path: str) -> List[Dict]:
    servers = []
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return servers

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 4:
                servers.append({
                    'host': parts[0],
                    'port': int(parts[1]) if len(parts) > 1 else 22,
                    'username': parts[2],
                    'password': parts[3]
                })
    return servers


def print_hardware_info(info: HardwareInfo):
    print(f"\n{'='*60}")
    print(f"主机: {info.hostname} ({info.ip})")
    print(f"{'='*60}")

    if info.error:
        print(f"❌ 错误: {info.error}")
        return

    print(f"📋 基本信息:")
    print(f"   操作系统: {info.os} {info.os_version}")
    print(f"   序列号: {info.sn}")
    print(f"   设备型号: {info.vendor} {info.product}")

    print(f"\n🖥️  CPU信息:")
    print(f"   型号: {info.cpu_model}")
    print(f"   数量: {info.cpu_num} 颗")
    print(f"   核心: {info.cpu_cores} 核")

    print(f"\n🧠 内存信息:")
    print(f"   总计: {info.memory_total} ({info.memory_bytes:,} bytes)")

    print(f"\n💾 硬盘信息:")
    print(f"   磁盘数: {info.disk_num}")
    print(f"   详情: {info.disk_info}")

    if info.gpu_num > 0:
        print(f"\n🎮 GPU信息:")
        print(f"   数量: {info.gpu_num}")
        print(f"   型号: {info.gpu_model}")
        print(f"   显存: {info.gpu_memory}")
    else:
        print(f"\n🎮 GPU信息: 无")

    print(f"\n⚡ 电源:")
    print(f"   额定功率: {info.power_rating}")


def main():
    parser = argparse.ArgumentParser(description='服务器硬件信息采集工具', formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 采集单台服务器
  python3 hw_collector.py -h 192.168.1.10 -u admin -p password123

  # 批量采集(文件格式: IP Port Username Password)
  python3 hw_collector.py -f servers.txt

  # 输出JSON格式(可用于CMDB导入)
  python3 hw_collector.py -h 192.168.1.10 -u admin -p password123 --json

  # 输出CSV格式
  python3 hw_collector.py -h 192.168.1.10 -u admin -p password123 --csv

服务器列表文件格式 (每行一个服务器):
  # IP Port Username Password
  192.168.1.10 22 root password123
  192.168.1.11 22 admin mypass
  192.168.1.12 2222 ubuntu secret
""")
    parser.add_argument('-H', '--host', help='服务器IP地址')
    parser.add_argument('-P', '--port', type=int, default=22, help='SSH端口 (默认: 22)')
    parser.add_argument('-u', '--username', help='SSH用户名')
    parser.add_argument('-p', '--password', help='SSH密码')
    parser.add_argument('-f', '--file', help='服务器列表文件')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--csv', action='store_true', help='输出CSV格式')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='SSH超时时间 (默认: 30秒)')
    parser.add_argument('-o', '--output', help='输出到文件')

    args = parser.parse_args()

    results = []

    if args.file:
        servers = servers_from_file(args.file)
        if not servers:
            print("没有找到有效的服务器配置")
            return
        print(f"将采集 {len(servers)} 台服务器...")
        results = collect_multiple_servers(servers)
    elif args.host and args.username and args.password:
        info = collect_single_server(args.host, args.port, args.username, args.password)
        results = [info]
    else:
        parser.print_help()
        return

    if args.json:
        output = '[\n' + ',\n'.join([r.to_json() for r in results]) + '\n]'
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"已保存到: {args.output}")
        else:
            print(output)
    elif args.csv:
        csv_header = "hostname,ip,os,cpu_model,cpu_num,memory,disk,gpu_model,gpu_num,sn,vendor,product\n"
        csv_lines = []
        for r in results:
            csv_lines.append(f'"{r.hostname}","{r.ip}","{r.os}","{r.cpu_model}",{r.cpu_num},"{r.memory}","{r.disk}","{r.gpu_model}",{r.gpu_num},"{r.sn}","{r.vendor}","{r.product}"')
        output = csv_header + '\n'.join(csv_lines)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"已保存到: {args.output}")
        else:
            print(output)
    else:
        for info in results:
            print_hardware_info(info)


if __name__ == '__main__':
    main()