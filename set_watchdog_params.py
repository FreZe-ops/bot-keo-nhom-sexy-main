import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
PYTHON = r'C:\tools\python\python.exe'
APP_DIR = r'C:\apps\bot-keo-nhom-bcr-main'

ssh.exec_command(f'{NSSM} set BCR-watchdog Application "{PYTHON}"')
ssh.exec_command(f'{NSSM} set BCR-watchdog AppParameters "{APP_DIR}\\session_watchdog_5m.py"')
ssh.exec_command(f'{NSSM} set BCR-watchdog AppDirectory "{APP_DIR}"')
ssh.exec_command(f'{NSSM} restart BCR-watchdog')

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} status BCR-watchdog')
print("Status BCR-watchdog:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
