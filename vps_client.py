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

def run_vps(cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    print(f"\n====================== COMMAND ======================\n{cmd}\n------------------------------------------------------")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=False)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err.strip():
        print(f"[STDERR]:\n{err}")
    ssh.close()
    return out

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whoami"
    run_vps(cmd)
