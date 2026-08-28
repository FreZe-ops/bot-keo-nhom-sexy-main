import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', port=22, username='administrator', password='uK?fdJ4Qo!7v', timeout=15)

files_to_check = [
    'bot1-err.log', 'bot2-err.log', 'bot3-err.log', 'bot4-err.log',
    'forward_bot_err.log', 'tele_out.log', 'watchdog_err.log'
]

for f in files_to_check:
    print(f"\n==================== {f} ====================")
    stdin, stdout, stderr = ssh.exec_command(f'powershell -Command "Get-Content C:\\apps\\bot-keo-nhom-bcr-main\\{f} -Tail 20"')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
