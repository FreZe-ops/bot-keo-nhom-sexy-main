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
sftp = ssh.open_sftp()

print("=== 1. WINDOWS SERVICES STATUS ===")
stdin, stdout, stderr = ssh.exec_command('C:\\tools\\nssm\\nssm-2.24\\win64\\nssm.exe status BCR-server & C:\\tools\\nssm\\nssm-2.24\\win64\\nssm.exe status BCR-session1 & C:\\tools\\nssm\\nssm-2.24\\win64\\nssm.exe status BCR-bot1 & C:\\tools\\nssm\\nssm-2.24\\win64\\nssm.exe status BCR-bot2 & C:\\tools\\nssm\\nssm-2.24\\win64\\nssm.exe status BCR-bot3 & C:\\tools\\nssm\\nssm-2.24\\win64\\nssm.exe status BCR-bot4')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== 2. RUNNING PROCESSES (NODE & PYTHON) ===")
stdin, stdout, stderr = ssh.exec_command('tasklist /FI "IMAGENAME eq node.exe" & tasklist /FI "IMAGENAME eq python.exe"')
print(stdout.read().decode('utf-8', errors='replace'))

def read_tail(filename, num_lines=20):
    path = f'C:/apps/bot-keo-nhom-bcr-main/logs/{filename}'
    print(f"\n==================== LOG: {filename} ====================")
    try:
        with sftp.open(path, 'r') as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 3000), 0)
            lines = f.read().decode('utf-8', errors='replace').splitlines()[-num_lines:]
            for l in lines:
                print(l)
    except Exception as e:
        print(f"Error reading {filename}: {e}")

read_tail('bot1-out.log', 15)
read_tail('bot1-err.log', 15)
read_tail('session1-out.log', 15)
read_tail('session1-err.log', 15)
read_tail('server-err.log', 15)

sftp.close()
ssh.close()
