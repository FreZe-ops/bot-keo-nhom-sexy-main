import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("1. Uploading session_watchdog_5m.py...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/session_watchdog_5m.py', 'C:/apps/bot-keo-nhom-bcr-main/session_watchdog_5m.py')
sftp.close()

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
PYTHON = r'C:\tools\python\python.exe'
APP_DIR = r'C:\apps\bot-keo-nhom-bcr-main'

print("2. Configuring BCR-watchdog service...")
ssh.exec_command(f'{NSSM} stop BCR-watchdog')
ssh.exec_command(f'{NSSM} remove BCR-watchdog confirm')

cmd_install = f'{NSSM} install BCR-watchdog "{PYTHON}" "{APP_DIR}\\session_watchdog_5m.py"'
stdin, stdout, stderr = ssh.exec_command(cmd_install)
print("Install:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.exec_command(f'{NSSM} set BCR-watchdog AppDirectory "{APP_DIR}"')
ssh.exec_command(f'{NSSM} set BCR-watchdog AppStdout "{APP_DIR}\\logs\\watchdog_out.log"')
ssh.exec_command(f'{NSSM} set BCR-watchdog AppStderr "{APP_DIR}\\logs\\watchdog_err.log"')
ssh.exec_command(f'{NSSM} set BCR-watchdog AppRestartDelay 5000')

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} start BCR-watchdog')
print("Start:", stdout.read().decode('utf-8', errors='replace').strip())

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} status BCR-watchdog')
print("Status BCR-watchdog:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
print("BCR-watchdog service installed and running on VPS!")
