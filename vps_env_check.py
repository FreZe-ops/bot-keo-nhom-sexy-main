import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=25)
for cmd in [
    'findstr /I "HEADLESS USE_FIREFOX DOMAIN" C:\\apps\\bot-keo-nhom-bcr-main\\.env',
    'powershell -Command "Get-Process firefox,chrome,chromium -ErrorAction SilentlyContinue | Select-Object Name,Id | Format-Table"',
]:
    stdin,stdout,stderr=ssh.exec_command(cmd)
    print('CMD:', cmd)
    print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
