import paramiko
import sys
import time

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

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

    # Xóa file session bị trùng IP
    ssh.exec_command(r'del /f /q C:\apps\bot-keo-nhom-bcr-main\user_session_84776956765*.session 2>nul')

    channel = ssh.invoke_shell()
    channel.send("set PATH=C:\\tools\\python;%PATH% & cd /d C:\\apps\\bot-keo-nhom-bcr-main & python bot_forward_runner.py --login bot_forward_1\r\n")

    buf = ""
    start = time.time()
    while time.time() - start < 35:
        if channel.recv_ready():
            data = channel.recv(2048).decode('utf-8', errors='replace')
            buf += data
            print(data, end="", flush=True)
            if "Nhập mã OTP:" in buf:
                break
        time.sleep(0.5)

    if len(sys.argv) > 1:
        otp_code = sys.argv[1].strip()
        print(f"\n>>> Đang gửi mã OTP {otp_code} lên VPS...")
        channel.send(f"{otp_code}\r\n")
        
        # Đợi kết quả login
        time.sleep(5)
        while channel.recv_ready():
            print(channel.recv(2048).decode('utf-8', errors='replace'), end="", flush=True)
            time.sleep(0.5)

    ssh.close()

if __name__ == '__main__':
    main()
