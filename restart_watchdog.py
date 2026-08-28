import paramiko
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=15)

cmds = [
    'powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*session_watchdog_5m*\' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"',
    'powershell -Command "Start-Process -WindowStyle Hidden -FilePath C:\\tools\\python\\python.exe -ArgumentList C:\\apps\\bot-keo-nhom-bcr-main\\session_watchdog_5m.py -WorkingDirectory C:\\apps\\bot-keo-nhom-bcr-main"',
]
for c in cmds:
    stdin, stdout, stderr = ssh.exec_command(c)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out.strip():
        print(out)
    if err.strip():
        print(err)

stdin, stdout, stderr = ssh.exec_command(
    'powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*session_watchdog_5m*\' } | Select-Object ProcessId, CreationDate"'
)
print('=== NEW WATCHDOG ===')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
