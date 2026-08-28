import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)

script = """
import os

p = r'C:\\apps\\bot-keo-nhom-bcr-main\\logs\\forward_bot_out.log'
if os.path.exists(p):
    with open(p, 'rb') as f:
        content = f.read().decode('utf-8', errors='replace')
    lines = content.split('\\n')
    for l in lines:
        if any(k in l for k in ['KHỞI ĐỘNG', 'Lịch chạy', 'Đăng nhập', 'bot_forward_', 'Trâm Anh', 'MINH', 'Hải Yến', 'AuthKey', 'Bắt đầu ca', 'HOÀN THÀNH']):
            print(l)
"""

stdin, stdout, stderr = ssh.exec_command(f'C:\\tools\\python\\python.exe -c "{script}"')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
