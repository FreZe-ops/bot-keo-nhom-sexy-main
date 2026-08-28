import paramiko
import sys
import time
import os

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
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = 'C:/apps/bot-keo-nhom-bcr-main'
NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

FILES = [
    'servicePuppeteer/session.js',
    'server.js',
    'session_watchdog_5m.py',
]

def main():
    print(f">>> Deploy capture smooth -> {HOST}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=20)
    sftp = ssh.open_sftp()

    for rel in FILES:
        local_path = os.path.join(LOCAL_DIR, rel.replace('/', os.sep))
        remote_path = f"{REMOTE_DIR}/{rel.replace(chr(92), '/')}"
        print(f"  upload {rel}")
        sftp.put(local_path, remote_path)
    sftp.close()

    # Headed Firefox on Windows — vào bàn ổn định hơn headless
    patch_env = (
        'powershell -Command "'
        f'$p=\\"{REMOTE_DIR}/.env\\"; '
        'if (Test-Path $p) { '
        '(Get-Content $p -Raw) '
        "-replace 'HEADLESS=1','HEADLESS=0' "
        "-replace 'HEADLESS=true','HEADLESS=0' "
        '| Set-Content $p -NoNewline }"'
    )
    ssh.exec_command(patch_env)

    ssh.exec_command(r'del /f /q C:\Users\Administrator\AppData\Local\Temp\sexy-account-*.lock 2>nul')

    print(">>> Restart BCR-server")
    ssh.exec_command(f'"{NSSM}" restart BCR-server')
    time.sleep(4)

    for i in range(1, 5):
        print(f">>> Restart BCR-session{i} (stagger {i * 5}s)")
        ssh.exec_command(f'"{NSSM}" restart BCR-session{i}')
        time.sleep(5)

    ssh.close()
    print("✅ Deploy xong — chờ 90s rồi audit...")

if __name__ == '__main__':
    main()
