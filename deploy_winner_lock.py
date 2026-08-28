import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("1. Uploading utilities/screenshotHelper.js...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/utilities/screenshotHelper.js', 'C:/apps/bot-keo-nhom-bcr-main/utilities/screenshotHelper.js')
print("2. Uploading servicePuppeteer/session.js...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/servicePuppeteer/session.js', 'C:/apps/bot-keo-nhom-bcr-main/servicePuppeteer/session.js')
print("3. Uploading bot_forward_runner.py...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/bot_forward_runner.py', 'C:/apps/bot-keo-nhom-bcr-main/bot_forward_runner.py')
sftp.close()

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
print("4. Restarting BCR-forward-bot...")
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart BCR-forward-bot')
print("BCR-forward-bot:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
print("Deployed winner-lock synchronization successfully!")
