import time
import urllib.request
import json
import subprocess
import os

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
API_BASE_URL = 'http://127.0.0.1:3201'
LOG_FILE = r'C:\apps\bot-keo-nhom-bcr-main\logs\auto_restart.log'

def log(msg):
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{now_str}][WATCHDOG-5M] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

def restart_session(session_num):
    s_name = f"BCR-session{session_num}"
    log(f"🚨 PHÁT HIỆN {s_name} (NS{session_num}) TREO/KHÔNG CÓ ẢNH > 5 PHÚT -> TIẾN HÀNH RESTART NGAY!")
    try:
        res = subprocess.run(f'"{NSSM}" restart {s_name}', capture_output=True, text=True, shell=True, timeout=30)
        log(f"  -> Kết quả restart {s_name}: {res.stdout.strip()}")
    except Exception as e:
        log(f"  -> Lỗi restart {s_name}: {e}")

def check_and_heal():
    for idx, ns in enumerate(['NS1', 'NS2', 'NS3', 'NS4'], 1):
        try:
            url = f"{API_BASE_URL}/api/get-active-table?nameService={ns}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.5) as r:
                data = json.loads(r.read().decode('utf-8'))
                table = data.get('activeTable')
                paused = data.get('paused', False)
                
                # Nếu không ở trong bàn hoặc bị pause
                if not table or table in ('NONE', 'LOBBY') or paused:
                    log(f"⚠️ {ns}: Chưa vào bàn (table={table}, paused={paused})")
                    # Sẽ được kiểm tra lại ở chu kỳ tiếp theo
                    continue
                
                # Kiểm tra độ mới của ảnh chụp bàn
                shot_url = f"{API_BASE_URL}/api/latest-screenshot?tableName={urllib.parse.quote(table)}"
                with urllib.request.urlopen(urllib.request.Request(shot_url), timeout=3.5) as sr:
                    sdata = json.loads(sr.read().decode('utf-8'))
                    if sdata.get('success') and sdata.get('data'):
                        stamp = sdata['data'].get('stampTime', 0)
                        age_s = time.time() - (stamp / 1000)
                        if age_s > 300: # Lâu quá 5 phút (300s) không có ảnh mới
                            log(f"❌ {ns} (Bàn {table}): Ảnh chụp đã cũ ({age_s:.1f}s > 300s) -> Cần restart")
def check_bot_services():
    services = ['BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4', 'BCR-forward-bot', 'BCR-server']
    for s in services:
        try:
            res = subprocess.run(f'"{NSSM}" status {s}', capture_output=True, text=True, shell=True, timeout=10)
            status = res.stdout.strip()
            if 'STOPPED' in status or 'PAUSED' in status:
                log(f"🚨 PHÁT HIỆN DỊCH VỤ {s} ĐANG BỊ DỪNG ({status}) -> TỰ ĐỘNG KHỞI ĐỘNG LẠI NGAY!")
                subprocess.run(f'"{NSSM}" start {s}', capture_output=True, text=True, shell=True, timeout=15)
        except Exception as e:
            log(f"⚠️ Lỗi check status {s}: {e}")

def main_loop():
    log("Khởi động Watchdog giám sát tự động 5 phút cho tất cả Session & Bot...")
    while True:
        try:
            check_and_heal()
            check_bot_services()
        except Exception as e:
            log(f"Lỗi vòng lặp giám sát: {e}")
        time.sleep(60)

if __name__ == '__main__':
    main_loop()
