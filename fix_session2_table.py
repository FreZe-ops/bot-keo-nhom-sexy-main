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

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

print("=== FIXING SESSION 2 PREFERRED TABLE (SET TO C02 VÌ C03 ĐANG ĐÓNG) ===")
# Đặt PREFERRED_TABLE=C02 cho session2
env_extra = (
    "PLAYWRIGHT_BROWSERS_PATH=C:\\ms-playwright\n"
    "ACCOUNT_INDEX=2\n"
    "PREFERRED_TABLE=C02\n"
    "DOTENV_CONFIG_PATH=C:\\apps\\bot-keo-nhom-bcr-main\\.env"
)
ssh.exec_command(f'{NSSM} set BCR-session2 AppEnvironmentExtra "{env_extra}"')

# Xóa các file lock cũ để bot không bị block
ssh.exec_command(r'del /f /q C:\apps\bot-keo-nhom-bcr-main\bot_NS*.lock 2>nul')

# Restart lại toàn bộ session và bot
print("=== RESTARTING SESSIONS 1, 2, 3, 4 & BOTS 1, 2, 3, 4 ===")
for s in ['BCR-session2', 'BCR-session3', 'BCR-bot2', 'BCR-bot3']:
    stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart {s}')
    print(f"Restarted {s}:", stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
print("Done fixing and restarting!")
