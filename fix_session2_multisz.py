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
$path = 'HKLM:\SYSTEM\CurrentControlSet\Services\BCR-session2\Parameters'
$val = [string[]]@('PLAYWRIGHT_BROWSERS_PATH=C:\ms-playwright', 'ACCOUNT_INDEX=2', 'PREFERRED_TABLE=C02', 'DOTENV_CONFIG_PATH=C:\apps\bot-keo-nhom-bcr-main\.env')
Set-ItemProperty -Path $path -Name 'AppEnvironmentExtra' -Value $val -Type MultiString
"""

print("=== SETTING MultiString REGISTRY AppEnvironmentExtra ===")
stdin, stdout, stderr = ssh.exec_command(f'powershell -Command "{ps_cmd}"')
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
stdin, stdout, stderr = ssh.exec_command(f'{NSSM} get BCR-session2 AppEnvironmentExtra')
print("VERIFY NSSM GET:")
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command(f'{NSSM} restart BCR-session2 & {NSSM} restart BCR-bot2')
print("RESTART STATUS:")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
