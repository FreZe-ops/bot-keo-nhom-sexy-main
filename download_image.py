import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

remote_path = 'C:/apps/bot-keo-nhom-bcr-main/public/screenshots/sexy_C05_R83_2026-08-25T06-53-43-683Z.png'
local_path = 'd:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/downloaded_c05_r83.png'
try:
    sftp.get(remote_path, local_path)
    print("Downloaded downloaded_c05_r83.png successfully!")
except Exception as e:
    print(f"Error downloading: {e}")

sftp.close()
ssh.close()
