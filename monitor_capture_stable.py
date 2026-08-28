"""Monitor VPS capture until 4 NS stable or timeout."""
import paramiko
import json
import time
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOST = "180.93.235.84"
USER = "administrator"
PASS = "uK?fdJ4Qo!7v"
API = "http://127.0.0.1:3201"
ROUNDS = 8
INTERVAL = 45


def api_get(path):
    with urllib.request.urlopen(API + path, timeout=6) as r:
        return json.loads(r.read().decode())


def remote_tail():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, 22, USER, PASS, timeout=20)
    remote = r'''
import os, re, glob, time
from urllib.request import urlopen
import json
out = {}
for ns in ["NS1","NS2","NS3","NS4"]:
    try:
        with urlopen(f"http://127.0.0.1:3201/api/get-active-table?nameService={ns}", timeout=4) as r:
            out[ns] = json.loads(r.read().decode())
    except Exception as e:
        out[ns] = {"err": str(e)}
shots = sorted(glob.glob(r"C:\apps\bot-keo-nhom-bcr-main\public\screenshots\sexy_*.png"), key=os.path.getmtime, reverse=True)[:6]
now = time.time()
print("TABLES", json.dumps(out))
print("SHOTS", "|".join(f"{os.path.basename(p)}:{int(now-os.path.getmtime(p))}s" for p in shots))
for i in range(1,5):
    p = rf"C:\apps\bot-keo-nhom-bcr-main\logs\session{i}-out.log"
    with open(p,"r",encoding="utf-8",errors="ignore") as f:
        lines = f.readlines()[-400:]
    cap_ok = sum(1 for l in lines if "[CAP OK]" in l or "Đã chụp ảnh thành công" in l)
    clear = sum(1 for l in lines if "[CLEAR]" in l and "xóa active_table" in l)
    fatal = sum(1 for l in lines if "FATAL UI" in l and "resetMain" in l)
    print(f"NS{i} cap_ok={cap_ok} clear={clear} fatal={fatal}")
'''
    sftp = ssh.open_sftp()
    with sftp.open("C:/apps/bot-keo-nhom-bcr-main/monitor_cap.py", "w") as f:
        f.write(remote.encode("utf-8"))
    sftp.close()
    stdin, stdout, stderr = ssh.exec_command(
        r"C:\tools\python\python.exe C:\apps\bot-keo-nhom-bcr-main\monitor_cap.py"
    )
    text = stdout.read().decode("utf-8", errors="replace")
    ssh.close()
    return text


def main():
    ok_streak = 0
    for rnd in range(1, ROUNDS + 1):
        print(f"\n=== Monitor round {rnd}/{ROUNDS} ===")
        try:
            text = remote_tail()
            print(text)
            ready = 0
            for line in text.splitlines():
                if line.startswith("TABLES "):
                    data = json.loads(line[7:])
                    for ns in ["NS1", "NS2", "NS3", "NS4"]:
                        t = (data.get(ns) or {}).get("activeTable")
                        if t and t not in ("NONE", "LOBBY", None):
                            ready += 1
            recent_shot = any(
                ":0s" in p or ":1s" in p or ":2s" in p or ":3s" in p
                for p in text.splitlines()
                if p.startswith("SHOTS ")
            ) or any(
                f":{s}s" in text
                for s in range(4, 90)
                if f":{s}s" in (text.split("SHOTS ")[1].split("\n")[0] if "SHOTS " in text else "")
            )
            if ready >= 3 and "fatal=0" in text:
                ok_streak += 1
                print(f"OK streak {ok_streak}/3 (ready={ready}/4)")
            else:
                ok_streak = 0
                print(f"Not stable yet (ready={ready}/4)")
            if ok_streak >= 3:
                print("\n✅ CAPTURE STABLE — 3 rounds with 3+ NS in table, no fatal reset")
                return 0
        except Exception as e:
            print("ERR", e)
            ok_streak = 0
        if rnd < ROUNDS:
            time.sleep(INTERVAL)
    print("\n⚠️ Chưa đạt ổn định sau monitor — cần kiểm tra thêm")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
