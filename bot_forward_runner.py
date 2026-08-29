import os
import sys
import json
import re
import sqlite3
import time
import random
import atexit
import ctypes
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import asyncio
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
)
from telethon.tl.types import Channel, Chat

# Terminal UTF-8 config on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

def log(msg, bot_name="BOT"):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{bot_name}] {msg}", flush=True)

ACCOUNTS_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tele_forward_accounts.json')
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public/screenshots')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3201')
API_KEY = os.getenv('API_KEY', 'your-static-api-key')

RESULT_IMAGE_DIRS = {
    'wincai': 'images/wincai',
    'losecai': 'images/losecai',
    'wincon': 'images/wincon',
    'losecon': 'images/losecon',
    'tie': 'images/tie',
}
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

TZ = timezone(timedelta(hours=7))  # GMT+7
SCHEDULE_INTERVAL = int(os.getenv('SCHEDULE_INTERVAL', '10'))
SCHEDULE_START_HOUR, SCHEDULE_START_MINUTE = 12, 0
SCHEDULE_END_HOUR, SCHEDULE_END_MINUTE = 22, 10
sent_slots = set()

def load_accounts_config():
    if not os.path.exists(ACCOUNTS_CONFIG_FILE):
        return []
    try:
        with open(ACCOUNTS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('accounts', [])
    except Exception as e:
        log(f"Lỗi đọc {ACCOUNTS_CONFIG_FILE}: {e}")
        return []

def get_account_by_id(account_id):
    accounts = load_accounts_config()
    for acc in accounts:
        if acc.get('id') == account_id or acc.get('phone') == account_id:
            return acc
    return None

def parse_bet_amount_numeric(label):
    """'500' -> 500, '5000' -> 5000. Label có % thì trả 0 (chế độ %)."""
    raw = str(label or "").strip()
    if "%" in raw:
        return 0
    try:
        return int(float(raw.replace(",", "")))
    except ValueError:
        return 0

def build_profit_result_text(bet_amount_label, norm_winner, norm_bet):
    """Thay Húp/Thua bằng: lợi nhuận ca này -500 / +500"""
    amount = parse_bet_amount_numeric(bet_amount_label)
    if amount <= 0:
        # Fallback % mode (giữ tương thích cũ)
        if norm_winner == "T" or not norm_winner:
            return "lợi nhuận ca này 0"
        if norm_winner == norm_bet:
            return "lợi nhuận ca này +10%"
        return "lợi nhuận ca này -10%"

    if norm_winner == "T" or not norm_winner:
        pnl = 0
    elif norm_winner == norm_bet:
        pnl = int(round(amount * 0.95)) if norm_bet == "B" else amount
    else:
        pnl = -amount

    if pnl > 0:
        return f"lợi nhuận ca này +{pnl}"
    if pnl < 0:
        return f"lợi nhuận ca này {pnl}"
    return "lợi nhuận ca này 0"

def build_virtual_profit_text(bet_amount_label, outcome):
    amount = parse_bet_amount_numeric(bet_amount_label) or 500
    if outcome == "WIN":
        pnl = amount
    elif outcome == "LOSS":
        pnl = -amount
    else:
        pnl = 0
    if pnl > 0:
        return f"lợi nhuận ca này +{pnl}"
    if pnl < 0:
        return f"lợi nhuận ca này {pnl}"
    return "lợi nhuận ca này 0"

def format_bet_text_with_amount(bet_text, bet_amount_label):
    amount = parse_bet_amount_numeric(bet_amount_label)
    if amount > 0:
        return f"{bet_text} {amount}"
    return f"{bet_text} {bet_amount_label}"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(ROOT_DIR, 'public', 'screenshots')

def resolve_screenshot_path(filepath):
    if not filepath:
        return None
    if os.path.isabs(filepath) and os.path.exists(filepath):
        return filepath
    candidates = [
        os.path.join(ROOT_DIR, filepath),
        os.path.join(ROOT_DIR, 'public', 'screenshots', os.path.basename(filepath)),
        os.path.join(ROOT_DIR, 'public', filepath),
        os.path.join(ROOT_DIR, 'screenshots', os.path.basename(filepath)),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def is_real_screenshot_file(filepath):
    if not filepath:
        return False
    resolved = resolve_screenshot_path(filepath)
    if not resolved or not os.path.exists(resolved):
        return False
    norm = str(resolved).replace("\\", "/").lower()
    name = os.path.basename(norm)
    if "/images/" in norm and "/screenshots/" not in norm:
        return False
    try:
        if os.path.getsize(resolved) < 40000:
            return False
    except OSError:
        return False
    return ("/screenshots/" in norm) or name.startswith("sexy_") or name.startswith("real_")

def extract_winner_from_filename(filepath):
    if not filepath:
        return None
    bname = os.path.basename(filepath).upper()
    if "_WB_" in bname or "_WB." in bname or "WINCAI" in bname:
        return "B"
    if "_WP_" in bname or "_WP." in bname or "WINCON" in bname:
        return "P"
    if "_WT_" in bname or "_WT." in bname or "TIE" in bname:
        return "T"
    return None

def get_latest_local_screenshot_for_table(table_name="C01", min_stamp_ms=None, exclude_file=None):
    search_dirs = [
        os.path.join(ROOT_DIR, 'public', 'screenshots'),
        os.path.join(ROOT_DIR, 'screenshots'),
    ]
    tbl_norm = table_name.lower()
    min_mtime = (min_stamp_ms / 1000.0) if min_stamp_ms else 0

    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        try:
            files = [
                os.path.join(sdir, f)
                for f in os.listdir(sdir)
                if f.lower().startswith('sexy_') and f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith('.')
            ]
            if not files:
                continue
            tbl_files = [f for f in files if f"_{tbl_norm}_" in f.lower() or f"{tbl_norm}_" in f.lower()]
            target_list = tbl_files if tbl_files else files
            target_list.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            for f in target_list:
                if is_real_screenshot_file(f) and extract_winner_from_filename(f):
                    if exclude_file and os.path.abspath(f) == os.path.abspath(exclude_file):
                        continue
                    if min_mtime > 0 and os.path.getmtime(f) < (min_mtime - 3):
                        continue
                    return f
        except Exception:
            pass
    return None

def get_real_screenshot_by_winner(table_name="C01", winner="B", exclude_file=None):
    """
    Tìm ảnh chụp THẬT từ Playwright trong public/screenshots khớp với bàn table_name và kết quả winner ('B'/'P'/'T').
    TUYỆT ĐỐI chỉ lấy ảnh thật bắt đầu bằng sexy_, không bao giờ lấy ảnh ảo!
    """
    search_dirs = [
        os.path.join(ROOT_DIR, 'public', 'screenshots'),
        os.path.join(ROOT_DIR, 'screenshots'),
    ]
    tbl_norm = table_name.lower()
    norm_win = normalize_side(winner)
    win_tag = "_wb" if norm_win == 'B' else ("_wp" if norm_win == 'P' else "_wt")

    candidates = []
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        try:
            files = [
                os.path.join(sdir, f)
                for f in os.listdir(sdir)
                if f.lower().startswith('sexy_') and f.lower().endswith(IMAGE_EXTENSIONS)
            ]
            for f in files:
                if exclude_file and os.path.abspath(f) == os.path.abspath(exclude_file):
                    continue
                fname = os.path.basename(f).lower()
                if (f"_{tbl_norm}_" in fname or f"{tbl_norm}_" in fname) and win_tag in fname:
                    candidates.append((os.path.getmtime(f), f))
        except Exception:
            pass

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    # Nếu không có ảnh đúng bàn đó có winner đó, lấy ảnh thật của bàn khác bất kỳ có đúng winner đó
    fallback_candidates = []
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        try:
            files = [
                os.path.join(sdir, f)
                for f in os.listdir(sdir)
                if f.lower().startswith('sexy_') and f.lower().endswith(IMAGE_EXTENSIONS)
            ]
            for f in files:
                if exclude_file and os.path.abspath(f) == os.path.abspath(exclude_file):
                    continue
                fname = os.path.basename(f).lower()
                if win_tag in fname:
                    fallback_candidates.append((os.path.getmtime(f), f))
        except Exception:
            pass

    if fallback_candidates:
        fallback_candidates.sort(key=lambda x: x[0], reverse=True)
        return fallback_candidates[0][1]

    return None

def get_any_table_preview_screenshot():
    """Lấy 1 ảnh bàn cược tổng quan Sexy Baccarat bất kỳ sạch sẽ từ thư mục ảnh chụp gần đây hoặc ảnh mẫu."""
    search_dirs = [
        os.path.join(ROOT_DIR, 'public', 'screenshots'),
        os.path.join(ROOT_DIR, 'screenshots'),
        os.path.join(ROOT_DIR, 'images', 'sexy'),
        os.path.join(ROOT_DIR, 'images'),
    ]
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        try:
            files = [
                os.path.join(sdir, f)
                for f in os.listdir(sdir)
                if f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith('.')
            ]
            if files:
                files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                return files[0]
        except Exception:
            pass
    for fb_type in ['wincai', 'wincon']:
        fb = get_fallback_image(fb_type)
        if fb and os.path.exists(fb):
            return fb
    return None

def get_virtual_result_image(bet_side, outcome):
    """
    Lấy ảnh kết quả từ folder ảnh ảo theo cửa cược (B/P) và kết quả (WIN/LOSS/TIE).
    - WIN: cược B -> lấy wincai, cược P -> lấy wincon
    - LOSS: cược B -> lấy wincon / losecai, cược P -> lấy wincai / losecon
    - TIE: lấy tie
    """
    if outcome == 'TIE':
        target_folder = 'images/tie'
    elif outcome == 'WIN':
        target_folder = 'images/wincai' if bet_side == 'B' else 'images/wincon'
    else:  # LOSS
        target_folder = 'images/wincon' if bet_side == 'B' else 'images/wincai'

    candidates = []
    for base_dir in [ROOT_DIR, r'C:\apps\bot-keo-nhom-bcr-main', os.path.dirname(os.path.abspath(__file__)), '.']:
        fpath = os.path.join(base_dir, target_folder)
        if os.path.isdir(fpath):
            imgs = [
                os.path.join(fpath, f)
                for f in os.listdir(fpath)
                if f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith('.')
            ]
            if imgs:
                candidates.extend(imgs)
                break

    if candidates:
        return random.choice(candidates)

    res_type = 'tie' if outcome == 'TIE' else ('wincai' if (outcome == 'WIN') == (bet_side == 'B') else 'wincon')
    return get_fallback_image(res_type)

def get_api_headers():
    return {
        'User-Agent': 'Mozilla/5.0',
        'x-api-key': API_KEY,
    }

async def get_healthy_active_sessions():
    """
    Quét toàn bộ các session cào (NS1..NS4) để tìm các bàn đang active trên Playwright.
    """
    healthy = []
    loop = asyncio.get_event_loop()
    
    def probe():
        res_list = []
        for ns in ['NS1', 'NS2', 'NS3', 'NS4']:
            try:
                url = f"{API_BASE_URL.rstrip('/')}/api/get-active-table?nameService={ns}"
                req = urllib.request.Request(url, headers=get_api_headers())
                with urllib.request.urlopen(req, timeout=2.5) as r:
                    data = json.loads(r.read().decode('utf-8'))
                    paused = data.get('paused', False)
                    table = str(data.get('activeTable') or '').upper().strip()
                    
                    if table and table not in ('NONE', 'LOBBY') and not paused:
                        res_list.append({
                            'name_service': ns,
                            'table': table,
                            'age_s': 0
                        })
            except Exception:
                pass
        return res_list

    try:
        healthy = await loop.run_in_executor(None, probe)
    except Exception as e:
        log(f"[WARN] Lỗi kiểm tra session health: {e}")
    return healthy

BOT_PREFERRED_SESSIONS = {
    'bot_forward_1': ['NS1', 'NS4', 'NS2', 'NS3'],
    'bot_forward_2': ['NS2', 'NS4', 'NS1', 'NS3'],
    'bot_forward_3': ['NS3', 'NS4', 'NS1', 'NS2'],
}
GLOBAL_BOT_TABLE_CLAIMS = {}
GLOBAL_CLAIM_LOCK = asyncio.Lock()

async def select_next_healthy_session(bot_id, previous_table=None, preferred_sessions=None, bot_name=""):
    """
    Phân bổ Session cho 3 Bot thật qua 4 Session (NS1, NS2, NS3, NS4).
    Đảm bảo 3 Bot luôn luôn vào 3 Bàn khác nhau 100%, tuyệt đối không trùng bàn!
    """
    async with GLOBAL_CLAIM_LOCK:
        healthy = await get_healthy_active_sessions()
        ns_map = {h['name_service']: h for h in healthy}
        
        # Danh sách các bàn đang bị bot khác sử dụng / khóa
        claimed_tables = {str(t).upper().strip() for b_id, t in GLOBAL_BOT_TABLE_CLAIMS.items() if b_id != bot_id and t}
        
        # Thứ tự ưu tiên riêng biệt cho từng bot để không đụng nhau
        pref_list = BOT_PREFERRED_SESSIONS.get(bot_id, ['NS1', 'NS2', 'NS3', 'NS4'])
        
        chosen = None
        for ns in pref_list:
            if ns in ns_map:
                cand = ns_map[ns]
                if cand['table'] not in claimed_tables:
                    chosen = cand
                    break
        
        if not chosen and healthy:
            unclaimed = [h for h in healthy if h['table'] not in claimed_tables]
            chosen = unclaimed[0] if unclaimed else healthy[0]
            
        if not chosen:
            fallback_map = {
                'bot_forward_1': ('NS1', 'C01'),
                'bot_forward_2': ('NS2', 'C02'),
                'bot_forward_3': ('NS3', 'C05')
            }
            fallback_ns, fallback_table = fallback_map.get(bot_id, ('NS4', 'C08'))
            GLOBAL_BOT_TABLE_CLAIMS[bot_id] = fallback_table
            log(f"[{bot_name}] Fallback về Bàn {fallback_table} ({fallback_ns})")
            return fallback_ns, fallback_table

        GLOBAL_BOT_TABLE_CLAIMS[bot_id] = chosen['table']
        
        log(f"[{bot_name or bot_id}] [SESSION ASSIGNED] Đã phân bổ Session {chosen['name_service']} - Bàn {chosen['table']} (Bàn bot khác đang chạy: {list(claimed_tables)})")
        return chosen['name_service'], chosen['table']

def get_latest_round(rounds):
    """Lấy ván cược MỚI NHẤT từ mảng totalRound (sắp xếp theo stampTime và id lớn nhất)."""
    if not isinstance(rounds, list) or not rounds:
        return None
    valid = []
    for r in rounds:
        if isinstance(r, dict):
            try:
                st = int(r.get('stampTime') or 0)
                rid = int(r.get('id') or 0)
                valid.append((st, rid, r))
            except (TypeError, ValueError):
                pass
    if not valid:
        return rounds[-1] if rounds else None
    valid.sort(key=lambda x: (x[0], x[1]))
    return valid[-1][2]

async def wait_for_fresh_bet_signal(table_name="C01", min_time_ms=0, max_wait_s=75):
    """
    Chờ một lệnh hô MỚI TINH phát sinh SAU mốc min_time_ms (sau khi đã chờ đủ 20s).
    Tuyệt đối không lấy lệnh cũ từ trước 20s đó.
    """
    start_t = time.time()
    q = urllib.parse.quote(str(table_name).strip().upper())
    url = f"{API_BASE_URL.rstrip('/')}/predict/get-table-by-name?tableName={q}"
    
    initial_stamp = 0
    initial_round_id = 0
    
    try:
        req = urllib.request.Request(url, headers=get_api_headers())
        with urllib.request.urlopen(req, timeout=3) as r:
            d = json.loads(r.read().decode('utf-8'))
            rounds = d.get('totalRound', [])
            latest_r = get_latest_round(rounds)
            if latest_r:
                initial_stamp = int(latest_r.get('stampTime') or 0)
                initial_round_id = int(latest_r.get('id') or 0)
    except Exception:
        pass

    log(f"⏳ Đang chờ lệnh hô MỚI từ nhóm thật bàn {table_name} (sau mốc {min_time_ms}, round hiện tại #{initial_round_id})...")

    while time.time() - start_t < max_wait_s:
        try:
            loop = asyncio.get_event_loop()
            req = urllib.request.Request(url, headers=get_api_headers())
            res_text = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=3).read().decode('utf-8')
            )
            res_data = json.loads(res_text)
            rounds = res_data.get('totalRound', [])
            latest_r = get_latest_round(rounds)
            if latest_r:
                cur_stamp = int(latest_r.get('stampTime') or 0)
                cur_id = int(latest_r.get('id') or 0)
                
                # Lệnh mới xuất hiện khi ván trước kết thúc sau min_time_ms hoặc có round mới
                if cur_stamp >= min_time_ms or cur_id > initial_round_id:
                    pct = res_data.get('percentCurrent', {})
                    round_signal = str(pct.get('Round') or '').upper()
                    banker_pct = float(pct.get('banker') or pct.get('B') or 50)
                    player_pct = float(pct.get('player') or pct.get('P') or 50)
                    
                    bet_side = 'B' if (banker_pct >= player_pct) else 'P'
                    if round_signal.startswith('P'):
                        bet_side = 'P'
                    elif round_signal.startswith('B'):
                        bet_side = 'B'

                    bet_text = '🔴 CÁI' if bet_side == 'B' else '🔵 CON'
                    log(f"✅ [FRESH BET SIGNAL] Nhận được lệnh hô MỚI bàn {table_name}: {bet_text} (Ván #{cur_id + 1}) sau {time.time() - start_t:.1f}s")
                    return bet_side, bet_text, len(rounds), cur_id
        except Exception:
            pass
        await asyncio.sleep(1.5)

    # Fallback nếu quá max_wait_s
    bet_side = random.choice(['B', 'P'])
    bet_text = '🔴 CÁI' if bet_side == 'B' else '🔵 CON'
    log(f"⚠️ [SIGNAL TIMEOUT] Dùng lệnh mặc định bàn {table_name}: {bet_text} (round #{initial_round_id})")
    return bet_side, bet_text, 0, initial_round_id

def normalize_side(val):
    if not val:
        return None
    s = str(val).strip().upper()
    if s in ('B', 'BANKER', 'CAI', 'CÁI') or s.startswith('B'):
        return 'B'
    if s in ('P', 'PLAYER', 'CON') or s.startswith('P'):
        return 'P'
    if s in ('T', 'TIE', 'HÒA', 'HOA') or s.startswith('T'):
        return 'T'
    return None

async def wait_for_table_screenshot_and_result(table_name="C01", bet_side="B", min_stamp_ms=None, initial_round_count=0, initial_round_id=0, exclude_shot=None, max_wait_s=75):
    """
    Chờ kết quả ván thật từ bàn và lấy ảnh chụp thật vừa hoàn thành của ĐÚNG ván đó.
    QUY TẮC ĐỐI CHIẾU CHUẨN XÁC:
    1. Bắt buộc kiểm tra Database bàn cược (/predict/get-table-by-name) xem đã có ván mới kết thúc chưa (id > initial_round_id hoặc số round tăng).
    2. CHỈ KHI DB ĐÃ MỞ THƯỞNG VÁN MỚI thì mới lấy kết quả và ảnh chụp tương ứng.
    3. Tuyệt đối không lấy ảnh chụp lúc đang đếm giây trước khi dealer lật bài.
    """
    start_time = time.time()
    q = urllib.parse.quote(str(table_name).strip().upper())
    predict_url = f"{API_BASE_URL.rstrip('/')}/predict/get-table-by-name?tableName={q}"
    shot_url = f"{API_BASE_URL.rstrip('/')}/api/latest-screenshot?tableName={q}"
    min_valid_stamp = min_stamp_ms or int(time.time() * 1000)
    
    db_winner = None
    db_round_id = None

    while time.time() - start_time < max_wait_s:
        try:
            loop = asyncio.get_event_loop()
            
            # 1. Kiểm tra Database bàn cược xem ván mới đã hoàn thành chưa (lấy ván mới nhất từ totalRound)
            req_db = urllib.request.Request(predict_url, headers=get_api_headers())
            res_db_text = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req_db, timeout=3).read().decode('utf-8')
            )
            res_db = json.loads(res_db_text)
            rounds = res_db.get('totalRound', [])
            latest_r = get_latest_round(rounds)
            if latest_r:
                cur_id = int(latest_r.get('id') or 0)
                cur_winner = normalize_side(latest_r.get('roadFormat'))
                cur_stamp = int(latest_r.get('stampTime') or 0)
                if (cur_id > initial_round_id or cur_stamp > min_valid_stamp or len(rounds) > initial_round_count) and cur_winner in ('B', 'P', 'T'):
                    if not db_winner:
                        db_winner = cur_winner
                        db_round_id = cur_id
                        log(f"[DB RESULT] Bàn {table_name} đã ghi nhận ván mới #{db_round_id} kết quả: {db_winner} (sau {time.time() - start_time:.1f}s)")

            # 2. CHỈ KHI DATABASE ĐÃ CÓ KẾT QUẢ VÁN MỚI thì mới tìm ảnh kết quả
            if db_winner:
                req_shot = urllib.request.Request(shot_url, headers=get_api_headers())
                res_shot_text = await loop.run_in_executor(
                    None,
                    lambda: urllib.request.urlopen(req_shot, timeout=3).read().decode('utf-8')
                )
                res_shot = json.loads(res_shot_text)
                if res_shot.get('success') and res_shot.get('data'):
                    shot_data = res_shot['data']
                    filepath = shot_data.get('filepath')
                    raw_winner = shot_data.get('resultWinner') or shot_data.get('winner')
                    shot_round = int(shot_data.get('roundNum') or 0)
                    stamp = int(shot_data.get('stampTime') or 0)
                    
                    if filepath and os.path.exists(filepath) and is_real_screenshot_file(filepath):
                        if not (exclude_shot and os.path.abspath(filepath) == os.path.abspath(exclude_shot)):
                            file_win = extract_winner_from_filename(filepath)
                            norm_win = normalize_side(raw_winner) or file_win
                            
                            # Ảnh phải chụp sau khi hô lệnh hoặc khớp đúng ván/kết quả mở thưởng
                            is_truly_new = (stamp >= (min_valid_stamp + 10000)) or (db_round_id and shot_round >= db_round_id) or (file_win == db_winner)
                            if is_truly_new and norm_win in ('B', 'P', 'T') and file_win:
                                log(f"[MATCH SHOT] Đã khớp ảnh chụp thật ván #{db_round_id}: {os.path.basename(filepath)} | Kết quả: {db_winner}")
                                return filepath, db_winner

                # Tìm ảnh cục bộ nếu API trả về trễ
                local_shot = get_latest_local_screenshot_for_table(table_name, min_stamp_ms=min_valid_stamp + 10000, exclude_file=exclude_shot)
                if local_shot:
                    return local_shot, db_winner
                
                real_match = get_real_screenshot_by_winner(table_name, db_winner, exclude_file=exclude_shot)
                if real_match:
                    return real_match, db_winner

        except Exception:
            pass
        await asyncio.sleep(1.5)

    # Nếu hết max_wait_s:
    if db_winner:
        real_match = get_real_screenshot_by_winner(table_name, db_winner, exclude_file=exclude_shot)
        if real_match:
            return real_match, db_winner

    real_match = get_real_screenshot_by_winner(table_name, bet_side, exclude_file=exclude_shot)
    return real_match, bet_side

def get_fallback_image(result_type):
    target_dir = RESULT_IMAGE_DIRS.get(result_type, 'images/wincai')
    if os.path.exists(target_dir):
        files = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith('.')
        ]
        if files:
            return random.choice(files)
    return None

def request_place_bet_api(table_name, bet_side, name_service=None, bet_amount=None):
    try:
        url = f"{API_BASE_URL.rstrip('/')}/api/place-bet"
        body = {
            "tableName": table_name,
            "betSide": bet_side,
            "side": bet_side,
        }
        if name_service:
            body["nameService"] = name_service
        if bet_amount:
            try:
                body["betAmount"] = float(bet_amount)
            except (ValueError, TypeError):
                pass
        data_bytes = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={**get_api_headers(), 'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=4) as res:
            res_json = json.loads(res.read().decode('utf-8'))
            log(f"🎰 [AUTO BET API] Đã gửi lệnh đặt cược tự động bàn {table_name} ({bet_side}) -> {res_json}")
            return res_json
    except Exception as ex:
        log(f"⚠️ [AUTO BET API ERROR] Không thể gửi lệnh đặt cược: {ex}")
        return None

SHARED_TELEGRAM_CLIENTS = {}

async def get_or_create_client(session_name, api_id, api_hash):
    if session_name in SHARED_TELEGRAM_CLIENTS:
        client = SHARED_TELEGRAM_CLIENTS[session_name]
        if not client.is_connected():
            await client.connect()
        return client
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    SHARED_TELEGRAM_CLIENTS[session_name] = client
    return client

class TelegramForwardBot:
    def __init__(self, config):
        self.config = config
        self.bot_id = config.get('id', 'bot_fw')
        self.name = config.get('name', self.bot_id)
        self.phone = config.get('phone', '').strip().replace(' ', '')
        self.api_id = int(config.get('api_id'))
        self.api_hash = config.get('api_hash', '').strip()
        self.twofa = config.get('twofa', '').strip()
        self.group_id = config.get('group_id')
        self.session_table = config.get('session_table', 'C01')
        self.name_service = config.get('name_service', 'NS1')
        self.source_username = config.get('source_username', 'frezeit')
        self.bet_amount_label = str(config.get('bet_amount_label', '10%')).strip()
        self.last_used_table = None
        self.is_running_round = False
        if self.bot_id == 'bot_forward_1':
            self.preferred_sessions = ['NS1']
        elif self.bot_id == 'bot_forward_2':
            self.preferred_sessions = ['NS2']
        elif self.bot_id == 'bot_forward_5':
            self.preferred_sessions = ['NS4']
        else:
            self.preferred_sessions = ['NS3']
        
        phone_digits = ''.join(c for c in self.phone if c.isdigit())
        self.session_name = f'user_session_{phone_digits}' if phone_digits else f'user_session_{self.bot_id}'
        self.client = None
        self.dialog_cache = {}

    def log(self, msg):
        log(msg, self.name)

    async def connect_and_login(self, interactive=True):
        self.client = await get_or_create_client(self.session_name, self.api_id, self.api_hash)
        
        if await self.client.is_user_authorized():
            me = await self.client.get_me()
            self.log(f"Đã đăng nhập: {me.first_name} (@{me.username}) | SĐT: {self.phone}")
            await self.warm_up_cache()
            return True

        if not interactive:
            self.log("[ERROR] Tài khoản chưa đăng nhập session. Vui lòng chạy lệnh login trước.")
            return False

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            self.log(f"Đang gửi mã OTP ({attempt}/{max_attempts}) tới số {self.phone}...")
            sent_code = await self.client.send_code_request(self.phone)
            self.log(f">>> ĐÃ GỬI MÃ OTP VỀ SỐ {self.phone}. Nhập mã:")
            code = input(f"[{self.name}] Nhập mã OTP: ").strip().replace(' ', '')
            try:
                await self.client.sign_in(phone=self.phone, code=code, phone_code_hash=sent_code.phone_code_hash)
                self.log("Đăng nhập thành công!")
                me = await self.client.get_me()
                self.log(f"Chào mừng: {me.first_name} (@{me.username})")
                await self.warm_up_cache()
                return True
            except SessionPasswordNeededError:
                self.log("Đang nhập mật khẩu 2FA...")
                pwd = self.twofa or input(f"[{self.name}] Nhập 2FA: ").strip()
                await self.client.sign_in(password=pwd)
                self.log("Đăng nhập 2FA thành công!")
                await self.warm_up_cache()
                return True
            except PhoneCodeExpiredError:
                self.log("Mã OTP hết hạn, đang thử lại...")
            except PhoneCodeInvalidError:
                self.log("Mã OTP không đúng, vui lòng nhập mã mới...")
            except Exception as e:
                self.log(f"Lỗi: {e}")
                if attempt == max_attempts:
                    raise
        return False

    async def warm_up_cache(self):
        self.dialog_cache = {}
        async for d in self.client.iter_dialogs():
            self.dialog_cache[str(d.id)] = d.entity
            raw = str(d.id)
            if raw.startswith('-100'):
                self.dialog_cache[raw[4:]] = d.entity
                self.dialog_cache[f"-{raw[4:]}"] = d.entity
            elif d.id > 0:
                self.dialog_cache[f"-100{d.id}"] = d.entity
                self.dialog_cache[f"-{d.id}"] = d.entity
            uname = getattr(d.entity, 'username', None)
            if uname:
                self.dialog_cache[uname.lower().lstrip('@')] = d.entity

    async def ensure_connected(self):
        if not self.client:
            self.client = await get_or_create_client(self.session_name, self.api_id, self.api_hash)
        if not self.client.is_connected():
            try:
                await self.client.connect()
            except Exception as e:
                self.log(f"[RECONNECT] Đang kết nối lại Telegram: {e}")

    async def resolve_entity(self, target):
        await self.ensure_connected()
        if not target:
            return None
        target_str = str(target).strip().lower().lstrip('@')
        if target_str in self.dialog_cache:
            return self.dialog_cache[target_str]
        try:
            try:
                return await self.client.get_entity(int(target))
            except (ValueError, TypeError):
                return await self.client.get_entity(target)
        except Exception:
            await self.warm_up_cache()
            return self.dialog_cache.get(target_str)

    async def execute_round(self, messages_to_send, exclude_tables=None):
        if not self.group_id:
            self.log("[ERROR] Chưa cấu hình group_id cho tài khoản này.")
            return

        if self.is_running_round:
            self.log("[BUSY] Đang trong ca chạy dở, bỏ qua lệnh gọi trùng lặp!")
            return

        await self.ensure_connected()
        entity = await self.resolve_entity(self.group_id)
        if not entity:
            self.log(f"[ERROR] Không tìm thấy nhóm ID={self.group_id}")
            return

        self.is_running_round = True
        try:
            # 0. TỰ ĐỘNG CHỌN BÀN KHỎE MẠNH VÀ KHÔNG TRÙNG VỚI BOT KHÁC
            selected_ns, selected_table = await select_next_healthy_session(
                bot_id=self.bot_id,
                previous_table=self.last_used_table,
                preferred_sessions=self.preferred_sessions,
                bot_name=self.name
            )
            self.name_service = selected_ns
            self.session_table = selected_table
            self.last_used_table = selected_table

            self.log(f"BẮT ĐẦU PHIÊN (Đồng bộ Session: {self.name_service} - Bàn {self.session_table} | Mức cược: {self.bet_amount_label})")

            async def forward_idx(index, label):
                if index < len(messages_to_send):
                    try:
                        await self.ensure_connected()
                        await self.client.forward_messages(entity, messages_to_send[index], silent=True, drop_author=True)
                        self.log(f"{label} (msg_id={messages_to_send[index].id}, index={index})")
                    except FloodWaitError as fe:
                        self.log(f"[FLOOD WAIT] Chờ {fe.seconds}s...")
                        await asyncio.sleep(fe.seconds + 1)
                        await self.ensure_connected()
                        await self.client.forward_messages(entity, messages_to_send[index], silent=True, drop_author=True)
                    except Exception as ex:
                        self.log(f"[LỖI FORWARD index {index}]: {ex}")

            async def send_text(txt, label):
                try:
                    await self.ensure_connected()
                    await self.client.send_message(entity, txt)
                    self.log(f"{label}: {txt}")
                except FloodWaitError as fe:
                    await asyncio.sleep(fe.seconds + 1)
                    await self.ensure_connected()
                    await self.client.send_message(entity, txt)
                except Exception as ex:
                    self.log(f"[LỖI SEND TEXT]: {ex}")

            # NẾU LÀ BOT CHẠY CHẾ ĐỘ ẢO (VIRTUAL / PRESET IMAGES & RATES)
            if self.config.get('is_virtual', False):
                self.log(f"BẮT ĐẦU PHIÊN ẢO (Tỉ lệ Thắng: {float(self.config.get('win_rate', 0.75))*100:.0f}% | Mức cược: {self.bet_amount_label})")

                # 1. Forward các tin mở đầu (Ảnh 5, Ảnh 1, Ảnh 2)
                opening_order = self.config.get('opening_order', [4, 0, 1])
                opening_delays = self.config.get('opening_delays', [20] * len(opening_order))
                for step_num, idx in enumerate(opening_order):
                    await forward_idx(idx, f"Tin mở đầu {step_num + 1}/{len(opening_order)}")
                    delay = opening_delays[step_num] if step_num < len(opening_delays) else 20
                    await asyncio.sleep(delay)

                # Gửi tin chuẩn bị vào lệnh (nếu có cấu hình)
                intro_text = self.config.get('send_intro_text', None)
                if intro_text:
                    await send_text(intro_text, "Đã gửi tin chuẩn bị vào lệnh")
                    await asyncio.sleep(20)

                # Gửi ảnh chụp bàn báo bàn sang nhóm báo bàn riêng (nếu có cấu hình)
                if self.config.get('send_table_preview'):
                    preview_shot = get_latest_local_screenshot_for_table(self.session_table) or get_any_table_preview_screenshot()
                    caption_template = self.config.get('send_table_preview_caption', '🎰 SẢNH SEXY BÀN : {table} 💎')
                    preview_caption = str(caption_template).replace('{table}', self.session_table)
                    
                    target_preview_group = self.config.get('table_preview_group_id', self.group_id)
                    target_preview_entity = await self.resolve_entity(target_preview_group)

                    if preview_shot and os.path.exists(preview_shot):
                        try:
                            self.log(f"Đang gửi ảnh bàn cược hiện tại kèm caption sang nhóm {target_preview_group}: {os.path.basename(preview_shot)}...")
                            await self.client.send_file(target_preview_entity or entity, preview_shot, caption=preview_caption)
                            self.log(f"✅ Đã gửi ảnh bàn cược kèm caption ({self.session_table}) sang nhóm {target_preview_group}")
                        except Exception as ex:
                            self.log(f"[LỖI GỬI ẢNH BÀN KÈM CAPTION]: {ex}")
                            if target_preview_entity:
                                await self.client.send_message(target_preview_entity, preview_caption)
                    else:
                        if target_preview_entity:
                            await self.client.send_message(target_preview_entity, preview_caption)
                    await asyncio.sleep(20)

                # 2. Chờ 20s rồi phát lệnh hô Con/Cái
                self.log("Chờ 20s trước khi phát lệnh hô...")
                await asyncio.sleep(20)

                bet_side = random.choice(['P', 'B'])  # P=Con, B=Cái
                bet_text_base = "🔵 CON" if bet_side == 'P' else "🔴 CÁI"
                bet_text_to_send = format_bet_text_with_amount(bet_text_base, self.bet_amount_label)
                await send_text(bet_text_to_send, "Đã gửi tin HÔ (Ảo)")

                # 3. Chờ 20s cho ván bài lật xong
                self.log(f"Đã hô lệnh ({bet_text_to_send}). Chờ cố định 20s cho ván bài lật xong...")
                await asyncio.sleep(20)

                # 4. Quyết định kết quả theo tỉ lệ (75% Thắng, 20% Thua, 5% Hòa)
                win_rate = float(self.config.get('win_rate', 0.75))
                loss_rate = float(self.config.get('loss_rate', 0.20))
                tie_rate = float(self.config.get('tie_rate', 0.05))

                roll = random.random()
                if roll < win_rate:
                    outcome = 'WIN'
                elif roll < (win_rate + loss_rate):
                    outcome = 'LOSS'
                else:
                    outcome = 'TIE'

                resolved_shot = get_virtual_result_image(bet_side, outcome)
                if resolved_shot and os.path.exists(resolved_shot):
                    try:
                        self.log(f"Đang gửi ảnh kết quả ({outcome}): {os.path.basename(resolved_shot)}...")
                        await self.client.send_file(entity, resolved_shot)
                        self.log(f"✅ Đã gửi ảnh kết quả ảo: {os.path.basename(resolved_shot)}")
                    except Exception as ex:
                        self.log(f"[LỖI GỬI ẢNH KẾT QUẢ ẢO]: {ex}")

                await asyncio.sleep(10)

                # 5. Gửi tin lợi nhuận ca này
                result_text = build_virtual_profit_text(self.bet_amount_label, outcome)

                self.log(f"[XÁC ĐỊNH KẾT QUẢ ẢO] Kèo hô={bet_text_to_send} | Outcome={outcome} | Trả tin: {result_text}")
                await send_text(result_text, f"Đã gửi tin KẾT QUẢ ẢO ({outcome}): {result_text}")
                await asyncio.sleep(20)

                # 6. Chốt ca bằng Ảnh 3 (index 2)
                ending_order = self.config.get('ending_order', [4, 5])
                ending_delays = self.config.get('ending_delays', [20, 20])
                for step_num, idx in enumerate(ending_order):
                    await forward_idx(idx, f"Tin kết thúc (tin thứ {idx + 1}, index {idx})")
                    delay = ending_delays[step_num] if step_num < len(ending_delays) else 20
                    await asyncio.sleep(delay)

                self.log(f"HOÀN THÀNH CA ẢO CHO NHÓM ({self.group_id}) THÀNH CÔNG!\n")
                return

            # NẾU LÀ BOT CHẠY CHẾ ĐỘ THẬT (SYNC VỚI TRANG GAME)

            # 1. Forward các tin mở đầu (index theo config, cách nhau 20s)
            opening_order = self.config.get('opening_order', [0, 1, 2, 3])
            opening_delays = self.config.get('opening_delays', [20, 20, 20, 20])
            for step_num, idx in enumerate(opening_order):
                await forward_idx(idx, f"Tin mở đầu {step_num + 1}/{len(opening_order)}")
                delay = opening_delays[step_num] if step_num < len(opening_delays) else 20
                await asyncio.sleep(delay)

            # Gửi tin text báo bàn tùy chỉnh (nếu cấu hình bật, VD: 🎲 BÀN Baccarat C05 🎲)
            if self.config.get('send_custom_table_text'):
                custom_table_text = str(self.config['send_custom_table_text']).replace('{table}', self.session_table)
                await send_text(custom_table_text, f"Đã gửi tin báo bàn {self.session_table}")
                await asyncio.sleep(20)

            # Gửi ảnh chụp bàn hiện tại KÈM CAPTION báo bàn cược (vào nhóm chính hoặc nhóm báo bàn riêng)
            preview_shot = None
            if self.config.get('send_table_preview'):
                preview_shot = get_latest_local_screenshot_for_table(self.session_table)
                caption_template = self.config.get('send_table_preview_caption', '🎰 SẢNH SEXY BÀN : {table} 💎')
                preview_caption = str(caption_template).replace('{table}', self.session_table)
                
                target_preview_group = self.config.get('table_preview_group_id', self.group_id)
                target_preview_entity = await self.resolve_entity(target_preview_group)

                if preview_shot and os.path.exists(preview_shot):
                    try:
                        self.log(f"Đang gửi ảnh bàn cược hiện tại kèm caption sang nhóm {target_preview_group}: {os.path.basename(preview_shot)}...")
                        await self.client.send_file(target_preview_entity or entity, preview_shot, caption=preview_caption)
                        self.log(f"✅ Đã gửi ảnh bàn cược kèm caption ({self.session_table}) sang nhóm {target_preview_group}")
                    except Exception as ex:
                        self.log(f"[LỖI GỬI ẢNH BÀN KÈM CAPTION]: {ex}")
                        if target_preview_entity:
                            await self.client.send_message(target_preview_entity, preview_caption)
                else:
                    if target_preview_entity:
                        await self.client.send_message(target_preview_entity, preview_caption)
                await asyncio.sleep(20)

            # 2. Chờ 20s trước, sau đó chỉ nhận lệnh hô MỚI TINH phát sinh sau 20s này
            wait_start_ms = int(time.time() * 1000)
            self.log(f"Chờ đủ 20s, sau đó lấy lệnh hô MỚI TINH phát sinh từ nhóm thật bàn {self.session_table}...")
            await asyncio.sleep(20)

            # Lấy lệnh hô MỚI phát sinh sau mốc 20s chờ (tuyệt đối không lấy lệnh cũ từ trước 20s)
            min_signal_time = wait_start_ms + 18000
            bet_side, bet_text, initial_round_count, initial_round_id = await wait_for_fresh_bet_signal(self.session_table, min_time_ms=min_signal_time)
            bet_time_ms = int(time.time() * 1000)  # Ghi nhận mốc thời gian hô lệnh

            # Định dạng lệnh hô
            bet_text_to_send = format_bet_text_with_amount(bet_text, self.bet_amount_label)

            await send_text(bet_text_to_send, f"Đã gửi tin HÔ (lấy trực tiếp theo bàn {self.session_table})")

            # ĐẶT CƯỢC TỰ ĐỘNG TRÊN TRANG GAME
            try:
                bet_amt = parse_bet_amount_numeric(self.bet_amount_label) or None
                request_place_bet_api(self.session_table, bet_side, self.name_service, bet_amt)
            except Exception as e:
                self.log(f"[AUTO BET ERROR]: {e}")

            # 3. CHỜ CỐ ĐỊNH ÍT NHẤT 20S để dealer chia bài và lật bài xong (không bao giờ lấy kết quả vội)
            self.log(f"Đã hô lệnh ({bet_text_to_send}). Chờ cố định 20s cho ván bài bàn {self.session_table} chia và lật bài xong...")
            await asyncio.sleep(20)

            # 4. Sau 20s: Lấy ẢNH THẬT và kết quả thực tế của ĐÚNG ván vừa cược xong (Đối chiếu trực tiếp DB)
            self.log(f"Đang lấy ảnh kết quả thật vừa mở thưởng bàn {self.session_table}...")
            real_screenshot, raw_winner = await wait_for_table_screenshot_and_result(
                self.session_table,
                bet_side,
                min_stamp_ms=bet_time_ms,
                initial_round_count=initial_round_count,
                initial_round_id=initial_round_id,
                exclude_shot=preview_shot,
                max_wait_s=65
            )
            resolved_shot = resolve_screenshot_path(real_screenshot)
            if not resolved_shot or (preview_shot and os.path.abspath(resolved_shot) == os.path.abspath(preview_shot)):
                resolved_shot = get_latest_local_screenshot_for_table(self.session_table, min_stamp_ms=bet_time_ms, exclude_file=preview_shot)
            if not resolved_shot or (preview_shot and os.path.abspath(resolved_shot) == os.path.abspath(preview_shot)):
                resolved_shot = get_real_screenshot_by_winner(self.session_table, raw_winner, exclude_file=preview_shot)

            if resolved_shot and os.path.exists(resolved_shot):
                try:
                    self.log(f"Đang gửi ảnh kết quả thật: {os.path.basename(resolved_shot)}...")
                    await self.client.send_file(entity, resolved_shot)
                    self.log(f"✅ Đã gửi ảnh kết quả thật bàn {self.session_table}: {os.path.basename(resolved_shot)}")
                except Exception as ex:
                    self.log(f"[LỖI GỬI ẢNH]: {ex}")
            else:
                self.log(f"[LỖI] Không tìm thấy file ảnh để gửi! (real={real_screenshot})")

            await asyncio.sleep(10)

            # 5. Trả tin kết quả chuẩn xác 100% theo ván thực tế:
            # ƯU TIÊN TUYỆT ĐỐI: Khóa kết quả 1:1 theo đúng file ảnh vừa gửi đi
            winner_from_filename = None
            if resolved_shot:
                bname = os.path.basename(resolved_shot).upper()
                if "_WB_" in bname or "_WB." in bname or "WINCAI" in bname:
                    winner_from_filename = "B"
                elif "_WP_" in bname or "_WP." in bname or "WINCON" in bname:
                    winner_from_filename = "P"
                elif "_WT_" in bname or "_WT." in bname or "TIE" in bname:
                    winner_from_filename = "T"

            norm_winner = winner_from_filename or normalize_side(raw_winner)
            norm_bet = normalize_side(bet_side)
            result_text = build_profit_result_text(self.bet_amount_label, norm_winner, norm_bet)

            self.log(f"[XÁC ĐỊNH KẾT QUẢ] Kèo hô={bet_text_to_send} ({norm_bet}) | Bàn mở ra={norm_winner} | Trả tin: {result_text}")
            await send_text(result_text, f"Đã gửi tin KẾT QUẢ (Ván bàn {self.session_table} ra {norm_winner})")
            await asyncio.sleep(20)

            # 6. Gửi tin 5 + 6 từ @frezeit (index 4, 5)
            ending_order = self.config.get('ending_order', [4, 5])
            ending_delays = self.config.get('ending_delays', [20, 20])
            for step_num, idx in enumerate(ending_order):
                await forward_idx(idx, f"Tin kết thúc (tin thứ {idx + 1}, index {idx})")
                delay = ending_delays[step_num] if step_num < len(ending_delays) else 20
                await asyncio.sleep(delay)

            self.log(f"HOÀN THÀNH CA CHO NHÓM ({self.group_id}) THEO BÀN {self.session_table} THÀNH CÔNG!\n")
        finally:
            GLOBAL_BOT_TABLE_CLAIMS.pop(self.bot_id, None)
            self.is_running_round = False

def generate_slots_for_config(interval=10, start_str="10:00", end_str="23:00"):
    slots = []
    sh, sm = map(int, start_str.split(':'))
    eh, em = map(int, end_str.split(':'))
    start_minutes = sh * 60 + sm
    end_minutes = eh * 60 + em
    minutes = start_minutes
    while minutes <= end_minutes:
        hour, minute = divmod(minutes, 60)
        slots.append(f"{hour:02d}:{minute:02d}")
        minutes += interval
    return slots

async def run_single_bot_schedule(bot, all_bots):
    interval = bot.config.get('interval_minutes', 10)
    start_str = bot.config.get('start_time', '10:00')
    end_str = bot.config.get('end_time', '23:00')
    
    slots = generate_slots_for_config(interval, start_str, end_str)
    slots_set = set(slots)
    sent_slots = set()
    
    bot.log(f"Lịch chạy: Từ {slots[0]} đến {slots[-1]} (mỗi {interval} phút, {len(slots)} ca/ngày)")
    
    while True:
        now = datetime.now(TZ)
        time_str = f"{now.hour:02d}:{now.minute:02d}"
        
        if time_str in slots_set:
            slot_key = now.strftime('%Y-%m-%d %H:%M')
            if slot_key not in sent_slots:
                if bot.is_running_round:
                    bot.log(f"[BUSY] Bot đang chạy ca trước, bỏ qua slot {slot_key} để tránh gửi lặp tin.")
                    sent_slots.add(slot_key)
                else:
                    bot.log(f"Bắt đầu ca {slot_key}...")
                    sent_slots.add(slot_key)
                    try:
                        await bot.ensure_connected()
                        source_entity = await bot.resolve_entity(bot.source_username)
                        if not source_entity:
                            bot.log(f"[ERROR] Không tìm thấy nguồn @{bot.source_username}")
                        else:
                            messages = []
                            async for m in bot.client.iter_messages(source_entity, limit=20):
                                messages.append(m)
                            messages.sort(key=lambda x: x.id)
                            
                            if len(messages) < 6:
                                bot.log(f"[WARN] Nguồn @{bot.source_username} chưa đủ 6 tin (cần tin 1-4 + tin 5-6).")
                            else:
                                # Lấy danh sách các bàn mà các bot khác đang sử dụng
                                other_tables = [
                                    b.session_table for b in all_bots 
                                    if b != bot and b.is_running_round and b.session_table
                                ]
                                await bot.execute_round(messages, exclude_tables=other_tables)
                    except Exception as e:
                        bot.log(f"[LỖI TRONG CA]: {e}")

        if now.hour == 0 and now.minute == 1:
            sent_slots = set()

        await asyncio.sleep(max(1, 60 - now.second))

async def main():
    parser = argparse.ArgumentParser(description="Multi-Account Telegram Forward Runner")
    parser.add_argument('--account', type=str, help="ID của tài khoản cần chạy (ví dụ bot_forward_1)")
    parser.add_argument('--login', type=str, help="Đăng nhập OTP cho tài khoản cụ thể (ví dụ bot_forward_1 hoặc bot_forward_2)")
    parser.add_argument('--all', action='store_true', help="Chạy toàn bộ tài khoản trong config song song")
    parser.add_argument('--run-now', action='store_true', default=False, help="Chạy ngay 1 ca test khi khởi động")
    args = parser.parse_args()

    accounts = load_accounts_config()
    if not accounts:
        log("[ERROR] Không tìm thấy tài khoản nào trong tele_forward_accounts.json")
        sys.exit(1)

    # Chế độ Login riêng từng tài khoản
    if args.login:
        acc = get_account_by_id(args.login)
        if not acc:
            log(f"[ERROR] Không tìm thấy tài khoản ID '{args.login}' trong tele_forward_accounts.json")
            sys.exit(1)
        bot = TelegramForwardBot(acc)
        await bot.connect_and_login(interactive=True)
        await bot.client.disconnect()
        return

    # Chọn danh sách bot cần chạy
    target_accounts = []
    if args.account:
        acc = get_account_by_id(args.account)
        if not acc:
            log(f"[ERROR] Không tìm thấy tài khoản ID '{args.account}'")
            sys.exit(1)
        target_accounts = [acc]
    else:
        target_accounts = accounts

    log(f"=== KHỞI ĐỘNG HỆ THỐNG FORWARD ĐA SESSION VỚI {len(target_accounts)} TÀI KHOẢN ===")
    bots = []
    for acc in target_accounts:
        b = TelegramForwardBot(acc)
        ok = await b.connect_and_login(interactive=False)
        if ok:
            bots.append(b)

    if not bots:
        log("[ERROR] Không có tài khoản nào đăng nhập thành công. Vui lòng đăng nhập trước bằng --login <id>")
        sys.exit(1)

    # Chạy ngay 1 ca test nếu bật --run-now
    if args.run_now:
        log("[RUN_NOW] Bắt đầu chạy ngay 1 ca kiểm tra đồng bộ động cho các bot...")
        for b in bots:
            if not b.group_id:
                b.log("[WARN] Bỏ qua ca test vì chưa cấu hình group_id.")
                continue
            source_entity = await b.resolve_entity(b.source_username)
            if source_entity:
                messages = []
                async for m in b.client.iter_messages(source_entity, limit=20):
                    messages.append(m)
                messages.sort(key=lambda x: x.id)
                if len(messages) >= 5:
                    other_tables = [other.session_table for other in bots if other != b and other.session_table]
                    asyncio.create_task(b.execute_round(messages, exclude_tables=other_tables))

    # Chạy schedule song song độc lập cho từng bot
    tasks = [run_single_bot_schedule(b, bots) for b in bots]
    try:
        await asyncio.gather(*tasks)
    finally:
        for b in bots:
            if b.client and b.client.is_connected():
                await b.client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Đã dừng runner.")
