import paramiko
import sys

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()
sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/submit_with_hash.py', 'C:/apps/bot-keo-nhom-bcr-main/submit_with_hash.py')
sftp.close()
ssh.close()
