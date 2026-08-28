import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

# Xóa session cũ bị lỗi AuthKeyDuplicatedError trên VPS
stdin, stdout, stderr = ssh.exec_command(r'del /f /q C:\apps\bot-keo-nhom-bcr-main\user_session_84776956765*.session 2>nul')

print(">>> [VPS] Bắt đầu xin mã OTP mới trực tiếp từ IP của VPS...")
channel = ssh.invoke_shell()
channel.send("set PATH=C:\\tools\\python;%PATH% & cd /d C:\\apps\\bot-keo-nhom-bcr-main & python bot_forward_runner.py --login bot_forward_1\r\n")

time_out = 30
buf = ""
import time
start = time.time()
while time.time() - start < time_out:
    if channel.recv_ready():
        data = channel.recv(1024).decode('utf-8', errors='replace')
        buf += data
        print(data, end="", flush=True)
        if "Nhập mã OTP:" in buf or ">>> ĐÃ GỬI MÃ OTP" in buf:
            print("\n[READY] Đã gửi OTP thành công! Đang chờ bạn nhập mã code...")
            break
    time.sleep(0.5)

ssh.close()
