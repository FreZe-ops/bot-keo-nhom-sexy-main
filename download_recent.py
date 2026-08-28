import paramiko

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
sftp = ssh.open_sftp()

files = [
    'sexy_C05_R13_2026-08-25T06-56-45-109Z.png',
    'sexy_C01_R20_2026-08-25T06-56-57-276Z.png',
    'sexy_C08_R66_2026-08-25T06-57-26-936Z.png'
]

for f in files:
    try:
        sftp.get(f'C:/apps/bot-keo-nhom-bcr-main/public/screenshots/{f}', f'd:/BOT KEO NHOM BCR/bot-keo-nhom-bcr-main/{f}')
        print(f"Downloaded {f}")
    except Exception as e:
        print(f"Error {f}: {e}")

sftp.close()
ssh.close()
