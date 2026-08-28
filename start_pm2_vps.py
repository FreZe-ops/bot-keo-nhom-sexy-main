import paramiko
import sys

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

def run(cmd):
    print(f"\n>>> [EXEC] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(f'set PATH=C:\\tools\\node;C:\\tools\\git\\cmd;C:\\tools\\python;C:\\tools\\python\\Scripts;C:\\tools\\mongodb\\bin;%PATH% & cd /d C:\\apps\\bot-keo-nhom-bcr-main & {cmd}')
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err.strip():
        print(f"[STDERR]: {err}")

# Chạy test thử bot_forward_runner trên VPS
run('C:\\tools\\python\\python.exe -c "import telethon; print(\'Telethon is OK on VPS\')"')

# Khởi động bot forward runner cho tài khoản Trâm Anh
run('pm2 delete bot_forward_runner 2>nul & pm2 start bot_forward_runner.py --name bot_forward_runner --interpreter C:\\tools\\python\\python.exe -- --all')
run('pm2 save')
run('pm2 list')

ssh.close()
