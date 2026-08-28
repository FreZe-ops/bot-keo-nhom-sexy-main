import paramiko
import os
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

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = 'C:/apps/bot-keo-nhom-bcr-main'

FILES_TO_UPLOAD = [
    'bot_forward_runner.py',
    'bot_multi_session.py',
    'groups_config.json',
    'tele_forward_accounts.json',
    'ecosystem.multi.config.js',
    'user_session_84776956765.session',
    'user_session_84776956765_ns1.session'
]

def main():
    print(f">>> [SFTP CONNECT] {USER}@{HOST}:{PORT}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    sftp = ssh.open_sftp()

    print(f"\n=== UPLOADING FILES TO VPS ({REMOTE_DIR}) ===")
    for filename in FILES_TO_UPLOAD:
        local_path = os.path.join(LOCAL_DIR, filename)
        if os.path.exists(local_path):
            remote_path = f"{REMOTE_DIR}/{filename}"
            print(f"Uploading: {filename} -> {remote_path}")
            sftp.put(local_path, remote_path)
            print(f"  -> SUCCESS ({os.path.getsize(local_path)} bytes)")
        else:
            print(f"  -> Skip (not found locally): {filename}")

    sftp.close()

    # Chạy kiểm tra trên VPS
    print("\n=== VERIFYING FILES ON VPS ===")
    stdin, stdout, stderr = ssh.exec_command(f'dir "{REMOTE_DIR}"')
    print(stdout.read().decode('utf-8', errors='replace'))

    ssh.close()
    print("\n✅ DEPLOY TO VPS COMPLETED!")

if __name__ == '__main__':
    main()
