import paramiko, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=20)
cmd = r'''powershell -Command "$lines = Get-Content C:\apps\bot-keo-nhom-bcr-main\logs\session1-out.log -Tail 5000; $lines | Select-String -Pattern 'SCREENSHOT|FATAL|LOBBY|REJECT|CROP|notify-screenshot|12-45|12-48' | Select-Object -Last 30 | ForEach-Object { $_.Line }"'''
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='replace')
print(out.encode('ascii', 'backslashreplace').decode())
ssh.close()
