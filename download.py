import paramiko
import os
from pathlib import Path
import hashlib
import json
import sys
import subprocess

# SRC_DIR = Path(os.path.dirname(__file__))
SRC_DIR = "/data/kongdejing/workspace/kdj/esp/kx-box3/"
MD5_STORAGE_FILE = os.path.join(os.path.dirname(__file__), 'md5_storage.json') # 用于存储MD5哈希值的JSON文件
different_files = []
# 定义闪存写入配置
download_flash_config = [
    ('0x0', 'D:\\esp\\box_factory_flash\\bootloader\\bootloader.bin'),
    ('0x8000', 'D:\\esp\\box_factory_flash\\partition_table\\partition-table.bin'),
    ('0x16000', 'D:\\esp\\box_factory_flash\\ota_data\\ota_data_initial.bin'),
    ('0x20000', 'D:\\esp\\box_factory_flash\\kx-box3.bin'),
    ('0x573000', 'D:\\esp\\box_factory_flash\\storage\\storage.bin'),
    ('0xa55000', 'D:\\esp\\box_factory_flash\\srmodels\\srmodels.bin'),
]

esptool_command = [
    'python', '-m', 'esptool',
    '--chip', 'esp32s3',
    '-b', '460800',
    '--before', 'default_reset',
    '--after', 'hard_reset',
    'write_flash',
    '--flash_mode', 'dio',
    '--flash_size', '16MB',
    '--flash_freq', '80m'
]



# 配置服务器信息和文件路径列表
server_ip = '10.122.86.70'
username = 'kongdejing'
password = 'H5VgZokC'
remote_file_info = [
    (f"{SRC_DIR}/build/bootloader/bootloader.bin", 'D:\\esp\\box_factory_flash\\bootloader'),
    (f"{SRC_DIR}/build/partition_table/partition-table.bin", 'D:\\esp\\box_factory_flash\\partition_table'),
    (f"{SRC_DIR}/build/ota_data_initial.bin", 'D:\\esp\\box_factory_flash\\ota_data'),
    (f"{SRC_DIR}/build/kx-box3.bin", 'D:\\esp\\box_factory_flash'),
    (f"{SRC_DIR}/build/storage.bin", 'D:\\esp\\box_factory_flash\\storage'),
    (f"{SRC_DIR}/build/srmodels/srmodels.bin", 'D:\\esp\\box_factory_flash\\srmodels'),
    # 添加更多文件路径和本地目录
]

# 跨平台颜色支持
def print_red(text):
    print(f"\033[91m{text}\033[0m", file=sys.stderr)  # ANSI转义码，用于在终端输出红色文本
 

def calculate_md5(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # 分块读取文件，并更新哈希对象
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def read_last_md5(md5_storage_file):
    """读取存储的上次MD5哈希值"""
    if os.path.exists(md5_storage_file):
        with open(md5_storage_file, 'r') as f:
            last_md5s = json.load(f)
    else:
        last_md5s = {}
    return last_md5s

def save_current_md5(md5_storage_file, current_md5s):
    """保存当前MD5哈希值"""
    with open(md5_storage_file, 'w') as f:
        json.dump(current_md5s, f, indent=4)

def download_file_from_sftp(server_ip, username, password, remote_file_info):

    last_md5s = read_last_md5(MD5_STORAGE_FILE)

    # 创建SFTP客户端
    transport = paramiko.Transport((server_ip, 22))
    try:
        # 连接到服务器# 使用SFTP会话
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        for remote_path, local_dir in remote_file_info:
            # 确保本地目录存在
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            
            # 获取远程文件名
            remote_file_name = os.path.basename(remote_path)
            local_file_path = os.path.join(local_dir, remote_file_name)
            
            # 下载文件 # 计算并打印MD5哈希值
            sftp.get(remote_path, local_file_path)        
            md5_value = calculate_md5(local_file_path)

            print(f"文件 {remote_file_name} 已成功下载到 {local_file_path}  MD5哈希值是: {md5_value}")

            # 使用文件的相对路径作为标识符（相对于所有本地目录的公共前缀）
            common_prefix = os.path.commonprefix([os.path.dirname(p[1]) for p in remote_file_info])
            file_identifier = os.path.relpath(local_file_path, start=common_prefix)
            
            if file_identifier in last_md5s and last_md5s[file_identifier] != md5_value:
                different_files.append(local_file_path)
                last_md5s[file_identifier] = md5_value
        
        save_current_md5(MD5_STORAGE_FILE, last_md5s)

        if different_files:
            print("\n以下文件的MD5哈希值已更改:")
            for file in different_files:
                print_red(file)
        else:
            print("\n所有文件的MD5哈希值均未更改。")


    except Exception as e:
        print(f"下载文件时出错: {e}")
    
    finally:
        # 关闭SFTP会话和连接
        sftp.close()
        transport.close()

def download_bin():
    if different_files == []:
        for address, filepath in download_flash_config:
            esptool_command.extend([address, filepath])
    else:
        for file in different_files:
            for address, filepath in download_flash_config:
                if filepath == file:
                    esptool_command.extend([address, filepath])
    try:
        result = subprocess.run(esptool_command, check=True, text=True, capture_output=True)
        print("Command executed successfully.")
        print(f"Output esptool_command: {esptool_command}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Command failed with error:")
        print(e.stderr)

if __name__ == '__main__':
    # 下载文件
    download_file_from_sftp(server_ip, username, password, remote_file_info)
    download_bin()