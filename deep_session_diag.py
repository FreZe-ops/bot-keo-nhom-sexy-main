import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)

script = r"""
import os, re, subprocess

def tail_grep(path, patterns, n=80):
    if not os.path.exists(path):
        return [f'MISSING {path}']
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    hits = [l.rstrip() for l in lines if any(p in l for p in patterns)]
    return hits[-n:] if hits else [f'(no match in {os.path.basename(path)})']

patterns = [
    'ENTER', 'IN ROOM', 'AUTO ENTER', 'CLICK TABLE', 'CHƯA VÀO', 'API NOTIFY',
    'resetMain', 'SHUTDOWN', 'HALL', 'LOGIN', 'probe', 'popup', 'BROWSER',
    'sessionInTableReady', 'SCREENSHOT', 'RECOVER', 'WATCHDOG', 'main function',
]

print('=== NSSM SESSION STATUS ===')
for i in range(1, 5):
    r = subprocess.run(
        [r'C:\tools\nssm\nssm-2.24\win64\nssm.exe', 'status', f'BCR-session{i}'],
        capture_output=True, text=True
    )
    print(f'BCR-session{i}: {r.stdout.strip()}')

base = r'C:\apps\bot-keo-nhom-bcr-main'
for i in range(1, 5):
    print(f'\n{"="*60}\nNS{i} KEY LOG LINES\n{"="*60}')
    for name in [f'logs/session{i}-out.log', f'logs_progress_ns{i}']:
        p = os.path.join(base, name)
        print(f'\n--- {name} ---')
        for line in tail_grep(p, patterns, 25):
            print(line)

print('\n=== NODE SESSION PROCESSES ===')
r = subprocess.run(
    'powershell -Command "Get-CimInstance Win32_Process -Filter \\"Name=\'node.exe\'\\" | Select-Object ProcessId,CommandLine"',
    capture_output=True, text=True, shell=True
)
print(r.stdout[:3000])
"""

sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/deep_diag.py', 'w') as f:
    f.write(script.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\deep_diag.py')
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))
ssh.close()
