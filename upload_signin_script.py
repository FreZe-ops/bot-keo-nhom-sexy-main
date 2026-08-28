import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

sftp.put('d:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/sign_in_bot2_vps.py', 'C:/apps/bot-keo-nhom-bcr-main/sign_in_bot2_vps.py')
sftp.close()
ssh.close()
print("Uploaded sign_in_bot2_vps.py to VPS!")
