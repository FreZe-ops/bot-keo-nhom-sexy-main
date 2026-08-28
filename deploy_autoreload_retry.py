import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("1. Uploading servicePuppeteer/session.js...")
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/servicePuppeteer/session.js', 'C:/apps/bot-keo-nhom-bcr-main/servicePuppeteer/session.js')
sftp.close()

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
print("2. Restarting BCR-session1..4...")
for s in ['BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4']:
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart {s}')
    print(f"Restart {s}:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
print("Deployed auto-reload and retry capture to VPS successfully!")
