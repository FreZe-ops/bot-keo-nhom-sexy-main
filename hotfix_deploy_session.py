import paramiko
import time
import os

HOST = '180.93.235.84'
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'
BASE = r'C:/apps/bot-keo-nhom-bcr-main'
NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
FILES = [
    ('servicePuppeteer/session.js', f'{BASE}/servicePuppeteer/session.js'),
    ('utilities/screenshotHelper.js', f'{BASE}/utilities/screenshotHelper.js'),
    ('utilities/lobbyTables.js', f'{BASE}/utilities/lobbyTables.js'),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PASS, timeout=20)
sftp = ssh.open_sftp()
for local_rel, remote in FILES:
    local = os.path.join(os.path.dirname(__file__), local_rel.replace('/', os.sep))
    sftp.put(local, remote)
    print('uploaded', local_rel)
sftp.close()
for i in range(1, 5):
    ssh.exec_command(f'"{NSSM}" restart BCR-session{i}')
    time.sleep(6)
ssh.close()
print('deployed session.js + screenshotHelper.js + lobbyTables.js')
