import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
services = [
    'BCR-server', 'BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4',
    'BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4', 'BCR-forward-bot', 'BCR-watchdog'
]

print("=== SERVICE STATUSES ===")
for s in services:
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} status {s}')
    st = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"{s}: {st}")

print("\n=== RUNNING PYTHON PROCESSES ===")
stdin, stdout, stderr = ssh.exec_command('powershell -Command "Get-Process python, node, firefox -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, CPU, WorkingSet"')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== FORWARD BOT LAST LOGS ===")
stdin, stdout, stderr = ssh.exec_command('powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\forward_bot_out.log -Tail 30"')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== FORWARD BOT LAST ERRORS ===")
stdin, stdout, stderr = ssh.exec_command('powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\forward_bot_err.log -Tail 30"')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n=== BOT1..4 LAST LOGS ===")
for b in [1, 2, 3, 4]:
    stdin, stdout, stderr = ssh.exec_command(f'powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\bot{b}-out.log -Tail 10"')
    print(f"--- bot{b}-out.log ---")
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
