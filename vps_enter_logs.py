import paramiko, sys, re
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('180.93.235.84', 22, 'administrator', 'uK?fdJ4Qo!7v', timeout=25)
remote = r'''
import re
pat = re.compile(r"CLICK TABLE|IN ROOM|card_pointer|legacy_pointer|mouse_|gettext|via=|BROWSER WARN|popup|probe|attempt|reserved|LOBBY DETECTED|CAP OK|zone_bet", re.I)
for i in range(1,5):
    p = rf"C:\apps\bot-keo-nhom-bcr-main\logs\session{i}-out.log"
    with open(p,"r",encoding="utf-8",errors="ignore") as f:
        lines = f.readlines()[-2500:]
    print(f"\n===== NS{i} =====")
    for l in lines:
        if pat.search(l):
            print(l.rstrip().encode("ascii","backslashreplace").decode())
'''
sftp = ssh.open_sftp()
with sftp.open('C:/apps/bot-keo-nhom-bcr-main/t_enter.py','w') as f: f.write(remote)
sftp.close()
stdin,stdout,stderr=ssh.exec_command(r'C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\t_enter.py')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
