import paramiko
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("==================== 1. KIỂM TRA HEALTH TẤT CẢ SESSION QUA API ====================")
stdin, stdout, stderr = ssh.exec_command(r'cd /d C:\apps\bot-keo-nhom-bcr-main & C:\tools\python\python.exe vps_health_check.py')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n==================== 2. TIẾN TRÌNH ĐANG CHẠY (NODE, PYTHON, CHROME) ====================")
stdin, stdout, stderr = ssh.exec_command('tasklist /FI "IMAGENAME eq node.exe" & tasklist /FI "IMAGENAME eq python.exe" & tasklist /FI "IMAGENAME eq chrome.exe" & tasklist /FI "IMAGENAME eq firefox.exe"')
print(stdout.read().decode('utf-8', errors='replace'))

def read_tail(filename, lines_count=12):
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{filename}'
    print(f"\n-------------------- {filename} --------------------")
    try:
        stat = sftp.stat(path)
        mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
        print(f"[Size: {stat.st_size} bytes | Sửa đổi lúc: {mod_time}]")
        with sftp.open(path, 'r') as f:
            f.seek(max(0, stat.st_size - 3000), 0)
            content = f.read().decode('utf-8', errors='replace').splitlines()[-lines_count:]
            for line in content:
                print(line)
    except Exception as e:
        print(f"Lỗi: {e}")

print("\n==================== 3. LOG LỖI & OUTPUT CÁC SESSION ====================")
for i in [1, 2, 3, 4]:
    read_tail(f'session{i}-out.log', 8)
    read_tail(f'session{i}-err.log', 8)

print("\n==================== 4. LOG LỖI & OUTPUT CÁC BOT KÉO CŨ ====================")
for i in [1, 2, 3, 4]:
    read_tail(f'bot{i}-out.log', 6)

read_tail('server-err.log', 10)

sftp.close()
ssh.close()
