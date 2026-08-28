import paramiko
import sys
import time

HOST = '180.93.235.84'
PORT = 22
USER = 'administrator'
PASS = 'uK?fdJ4Qo!7v'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)

ps_cmd = r"""
$envList = @(
    "PLAYWRIGHT_BROWSERS_PATH=C:\ms-playwright",
    "ACCOUNT_INDEX=2",
    "PREFERRED_TABLE=C02",
    "DOTENV_CONFIG_PATH=C:\apps\bot-keo-nhom-bcr-main\.env"
)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\BCR-session2\Parameters" -Name "AppEnvironmentExtra" -Value $envList
"""

print("=== SETTING REGISTRY AppEnvironmentExtra FOR BCR-session2 ===")
stdin, stdout, stderr = ssh.exec_command(f'powershell -Command "{ps_cmd}"')
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'

# Xóa lock tạm của account 2 nếu có
ssh.exec_command(r'del /f /q C:\Users\ADMINI~1\AppData\Local\Temp\sexy-account-*.lock 2>nul')

print("=== RESTARTING BCR-session2 & BCR-bot2 ===")
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart BCR-session2 & {NSSM} restart BCR-bot2')
print(stdout.read().decode('utf-8', errors='replace'))

time.sleep(5)

# Kiểm tra lại environment
print("=== VERIFYING AppEnvironmentExtra ===")
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get BCR-session2 AppEnvironmentExtra')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print("Done fixing session2!")
