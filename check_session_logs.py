import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)
for logname in ['session1-out.log', 'session2-out.log', 'session3-out.log', 'session4-out.log']:
    stdin, stdout, stderr = ssh.exec_command(f'powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\{logname} -Tail 25"')
    print(f'=== {logname} ===')
    print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
