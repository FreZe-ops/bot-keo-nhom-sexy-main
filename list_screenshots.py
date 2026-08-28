import paramiko
import sys
import json

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("Listing screenshots dir:")
try:
    files = sftp.listdir('C:/apps/bot-keo-nhom-bcr-main/screenshots')
    for f in sorted(files)[-10:]:
        print(f)
except Exception as e:
    print(f"Error: {e}")

sftp.close()
ssh.close()
