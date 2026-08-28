import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

cmd = r'schtasks /create /tn "BCR_Watchdog_5M" /tr "C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\session_watchdog_5m.py" /sc MINUTE /mo 2 /ru "SYSTEM" /f'
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Create Scheduled Task:", stdout.read().decode('utf-8', errors='replace').strip())

cmd_run = r'schtasks /run /tn "BCR_Watchdog_5M"'
stdin, stdout, stderr = ssh.exec_command(cmd_run)
print("Run Scheduled Task:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
