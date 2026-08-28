import paramiko
HOST = "180.93.235.84"
USER = "administrator"
PASS = "uK?fdJ4Qo!7v"
NSSM = r"C:\tools\nssm\nssm-2.24\win64\nssm.exe"
ENV_PATH = r"C:\apps\bot-keo-nhom-bcr-main\.env"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, 22, USER, PASS, timeout=25)
sftp = ssh.open_sftp()
with sftp.open(ENV_PATH, "r") as f:
    env = f.read().decode("utf-8", errors="replace")
env = env.replace("USE_FIREFOX=0", "USE_FIREFOX=1")
with sftp.open(ENV_PATH, "w") as f:
    f.write(env.encode("utf-8"))
sftp.close()
ssh.exec_command(f'"{NSSM}" restart BCR-session1')
print("reverted USE_FIREFOX=1 + restarted NS1")
ssh.close()
