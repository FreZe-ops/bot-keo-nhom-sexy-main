import sys
import os
import time
import subprocess
import json
import urllib.request
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
API_BASE_URL = 'http://127.0.0.1:3201'
LOG_FILE = r'C:\apps\bot-keo-nhom-bcr-main\logs\auto_restart.log'

def log(msg):
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{now_str}][WATCHDOG] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

def restart_session(ns):
    session_num = ns.replace('NS', '').strip()
    s_name = f"BCR-session{session_num}"
    log(f"🚨 RESTART {s_name} ({ns})...")
    try:
        res = subprocess.run(f'"{NSSM}" restart {s_name}', capture_output=True, text=True, shell=True, timeout=30)
        log(f"  -> Ket qua restart {s_name}: {res.stdout.strip()}")
    except Exception as e:
        log(f"  -> Loi restart {s_name}: {e}")

session_not_in_table_count = {}

def check_and_heal():
    for ns in ['NS1', 'NS2', 'NS3', 'NS4']:
        try:
            url = f"{API_BASE_URL}/api/get-active-table?nameService={ns}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.5) as r:
                data = json.loads(r.read().decode('utf-8'))
                table = data.get('activeTable')
                paused = data.get('paused', False)
                
                # Nếu không ở trong bàn hoặc bị pause
                if not table or table in ('NONE', 'LOBBY') or paused:
                    count = session_not_in_table_count.get(ns, 0) + 1
                    session_not_in_table_count[ns] = count
                    log(f"⚠️ {ns}: Chua vao ban (lan {count}/4, table={table}, paused={paused})")
                    if count >= 4: # Cho phep toi thieu 3 phut de login va load sanh truoc khi restart
                        log(f"🚨 {ns}: Qua 3 phut chua vao ban -> Restart {ns}")
                        session_not_in_table_count[ns] = 0
                        restart_session(ns)
                    continue
                else:
                    session_not_in_table_count[ns] = 0
                
                # Kiểm tra độ mới của ảnh chụp bàn
                shot_url = f"{API_BASE_URL}/api/latest-screenshot?tableName={urllib.parse.quote(str(table))}"
                with urllib.request.urlopen(urllib.request.Request(shot_url), timeout=3.5) as sr:
                    sdata = json.loads(sr.read().decode('utf-8'))
                    if sdata.get('success') and sdata.get('data'):
                        stamp = sdata['data'].get('stampTime', 0)
                        age_s = time.time() - (stamp / 1000)
                        if age_s > 300: # Lâu quá 5 phút không có ảnh mới
                            log(f"❌ {ns} (Ban {table}): Anh chup da cu ({age_s:.1f}s > 300s) -> Restart {ns}")
                            restart_session(ns)
        except Exception as e:
            log(f"⚠️ Loi kiem tra session {ns}: {e}")

def check_bot_services():
    services = [
        'BCR-server',
        'BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4',
        'BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4',
        'BCR-forward-bot'
    ]
    for s in services:
        try:
            res = subprocess.run(f'"{NSSM}" status {s}', capture_output=True, text=True, shell=True, timeout=10)
            status = res.stdout.strip()
            if 'STOPPED' in status or 'PAUSED' in status:
                log(f"🚨 PHAT HIEN DICH VU {s} DANG BI DUNG ({status}) -> TU DONG KHOI DONG LAI NGAY!")
                subprocess.run(f'"{NSSM}" start {s}', capture_output=True, text=True, shell=True, timeout=15)
        except Exception as e:
            log(f"⚠️ Loi check status {s}: {e}")

def main_loop():
    log("Khoi dong Watchdog 24/7 tu dong giam sat va tu phuc hoi...")
    while True:
        try:
            check_and_heal()
            check_bot_services()
        except Exception as e:
            log(f"Loi vong lap giam sat: {e}")
        time.sleep(45)

if __name__ == '__main__':
    main_loop()
