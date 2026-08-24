import os
import sys
import time
import subprocess
import glob

NSSM = r'C:\tools\nssm\nssm-2.24\win64\nssm.exe'
LOG_FILE = r'C:\apps\bot-keo-nhom-bcr-main\logs\auto_restart.log'

def log(msg):
    now_str = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{now_str}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=30)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def clean_locks():
    log("🧹 Đang dọn dẹp các file lock tạm...")
    temp_dir = os.environ.get('TEMP', r'C:\Users\Administrator\AppData\Local\Temp')
    pattern = os.path.join(temp_dir, 'sexy-account-*.lock')
    for f in glob.glob(pattern):
        try:
            os.remove(f)
            log(f"  - Đã xóa lock: {os.path.basename(f)}")
        except Exception as e:
            log(f"  - Không xóa được {f}: {e}")

def restart_sessions():
    log("🚀 ================= BẮT ĐẦU TỰ ĐỘNG RESTART TẤT CẢ SESSION (CHU KỲ 2 TIẾNG) =================")
    clean_locks()
    
    sessions = ['BCR-session1', 'BCR-session2', 'BCR-session3', 'BCR-session4']
    bots = ['BCR-bot1', 'BCR-bot2', 'BCR-bot3', 'BCR-bot4']
    
    # 1. Restart từng session tuần tự (stagger 8s) để không bị đụng IP/login
    for i, s in enumerate(sessions, 1):
        log(f"🔄 Đang restart {s} (Session {i}/4)...")
        out = run_cmd(f'"{NSSM}" restart {s}')
        log(f"  -> Kết quả {s}: {out}")
        time.sleep(8)
        
    log("⏳ Chờ 10s cho các session Playwright vào bàn trước khi làm mới bot...")
    time.sleep(10)
    
    # 2. Restart các bot kéo để kết nối ngay với bàn mới
    for b in bots:
        log(f"🔄 Đang restart bot {b}...")
        out = run_cmd(f'"{NSSM}" restart {b}')
        log(f"  -> Kết quả {b}: {out}")
        time.sleep(2)
        
    log("✅ ================= HOÀN THÀNH RESTART TẤT CẢ SESSION & BOT THÀNH CÔNG =================\n")

if __name__ == '__main__':
    restart_sessions()
