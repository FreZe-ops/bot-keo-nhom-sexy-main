import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

print("Listing images/sexy on VPS:")
try:
    files = sftp.listdir('C:/apps/bot-keo-nhom-bcr-main/images/sexy')
    for f in sorted(files)[-15:]:
        print(f)
except Exception as e:
    print(f"Error: {e}")

sftp.close()
ssh.close()
