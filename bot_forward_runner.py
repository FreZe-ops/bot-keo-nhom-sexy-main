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

def is_real_screenshot_file(filepath):
    if not filepath or not os.path.exists(filepath):
        return False
    norm = str(filepath).replace("\\", "/").lower()
    name = os.path.basename(norm)
    if "/images/" in norm and "/screenshots/" not in norm:
        return False
    try:
        if os.path.getsize(filepath) < 40000:
            return False
    except OSError:
        return False
    return ("/screenshots/" in norm) or name.startswith("sexy_") or name.startswith("real_")

def get_latest_local_screenshot_for_table(table_name="C01"):
    if not os.path.exists(SCREENSHOT_DIR):
        return None
    try:
        tbl_norm = table_name.lower()
        files = [
            os.path.join(SCREENSHOT_DIR, f)
            for f in os.listdir(SCREENSHOT_DIR)
            if f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith('.')
        ]
        if not files:
            return None
        tbl_files = [f for f in files if f"_{tbl_norm}_" in f.lower() or f"{tbl_norm}_" in f.lower()]
        target_list = tbl_files if tbl_files else files
        target_list.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for f in target_list[:5]:
            if is_real_screenshot_file(f):
                return f
    except Exception:
        pass
    return None

def get_api_headers():
    return {
        'User-Agent': 'Mozilla/5.0',
        'x-api-key': API_KEY,
    }

async def get_healthy_active_sessions():
    """
    Quét toàn bộ các session cào (NS1..NS4) để tìm các bàn đang chạy mượt,
    không bị treo, không bị paused, và có ảnh chụp mới nhất (< 120s).
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
                        # Kiểm tra ảnh chụp bàn mới nhất
                        shot_url = f"{API_BASE_URL.rstrip('/')}/api/latest-screenshot?tableName={urllib.parse.quote(table)}"
                        shot_req = urllib.request.Request(shot_url, headers=get_api_headers())
                        with urllib.request.urlopen(shot_req, timeout=2.5) as sr:
                            sdata = json.loads(sr.read().decode('utf-8'))
                            if sdata.get('success') and sdata.get('data'):
                                sinfo = sdata['data']
                                stamp = int(sinfo.get('stampTime') or 0)
                                age_s = ((time.time() * 1000) - stamp) / 1000.0 if stamp else 9999
                                filepath = sinfo.get('filepath')
                                # Nếu ảnh mới trong vòng 150s và là file thật -> Session khỏe mạnh
                                if age_s < 150 and is_real_screenshot_file(filepath):
                                    res_list.append({
                                        'name_service': ns,
                                        'table': table,
                                        'age_s': age_s
                                    })
            except Exception:
                pass
        return res_list

    try:
        healthy = await loop.run_in_executor(None, probe)
    except Exception as e:
        log(f"[WARN] Lỗi kiểm tra session health: {e}")
    return healthy

async def select_next_healthy_session(previous_table=None):
    """
    Chọn 1 bàn cào mượt mà nhất, tự động đổi sang bàn khác với ca trước.
    """
    healthy = await get_healthy_active_sessions()
    
    if not healthy:
        log(f"[WARN] Không tìm thấy session nào đạt chuẩn sức khỏe. Fallback về Bàn C01 (NS1).")
        return 'NS1', 'C01'

    # Sắp xếp theo độ tươi mới của ảnh
    healthy.sort(key=lambda x: x['age_s'])

    # Lọc các bàn khác với bàn ở ca trước (để đổi bàn liên tục mỗi 10 phút)
    candidates = [h for h in healthy if h['table'] != str(previous_table).upper().strip()]
    if not candidates:
        candidates = healthy  # Nếu chỉ có 1 bàn duy nhất thì vẫn dùng bàn đó

    chosen = random.choice(candidates)
    log(f"[DYNAMIC ROTATION] Đã chọn Session {chosen['name_service']} - Bàn {chosen['table']} (Ảnh mới cách {chosen['age_s']:.1f}s, khác ca trước: '{previous_table}')")
    return chosen['name_service'], chosen['table']

async def get_live_table_prediction(table_name="C01", name_service="NS1"):
    """
    Lấy kèo dự đoán thật từ session / bàn cược đang chạy trên Playwright.
    """
    try:
        q = urllib.parse.quote(str(table_name).strip().upper())
        url = f"{API_BASE_URL.rstrip('/')}/predict/get-table-by-name?tableName={q}"
        req = urllib.request.Request(url, headers=get_api_headers())
        loop = asyncio.get_event_loop()
        res_text = await loop.run_in_executor(
            None,
            lambda: urllib.request.urlopen(req, timeout=3).read().decode('utf-8')
        )
        res_data = json.loads(res_text)
        payload = res_data.get('data', res_data) if isinstance(res_data, dict) else {}
        
        # Đọc tỷ lệ dự đoán Banker / Player
        pct = payload.get('percentCurrent', {})
        banker_pct = float(pct.get('banker') or pct.get('B') or 50)
        player_pct = float(pct.get('player') or pct.get('P') or 50)
        
        if banker_pct > player_pct:
            return 'B', '🔴 CÁI'
        elif player_pct > banker_pct:
            return 'P', '🔵 CON'
    except Exception as e:
        log(f"[WARN] Lỗi lấy dự đoán live {table_name}: {e}. Dùng thuật toán cầu.")

    # Fallback tự chọn
    is_cai = random.choice([True, False])
    return ('B', '🔴 CÁI') if is_cai else ('P', '🔵 CON')

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

async def wait_for_table_screenshot_and_result(table_name="C01", bet_side="B", min_stamp_ms=None, max_wait_s=45):
    """
    Chờ kết quả ván thật từ bàn và lấy ảnh chụp thật vừa hoàn thành của ván đó (stamp >= min_stamp_ms).
    """
    start_time = time.time()
    url = f"{API_BASE_URL.rstrip('/')}/api/latest-screenshot?tableName={urllib.parse.quote(table_name)}"
    
    while time.time() - start_time < max_wait_s:
        try:
            req = urllib.request.Request(url, headers=get_api_headers())
            loop = asyncio.get_event_loop()
            res_text = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=3).read().decode('utf-8')
            )
            res_data = json.loads(res_text)
            if res_data.get('success') and res_data.get('data'):
                shot_data = res_data['data']
                filepath = shot_data.get('filepath')
                stamp = int(shot_data.get('stampTime') or 0)
                raw_winner = shot_data.get('resultWinner') or shot_data.get('winner')
                
                # Đảm bảo ảnh được chụp SAU thời điểm hô lệnh (đúng ván vừa hô)
                if min_stamp_ms and stamp < min_stamp_ms:
                    await asyncio.sleep(2)
                    continue
                
                if filepath and os.path.exists(filepath) and is_real_screenshot_file(filepath):
                    return filepath, raw_winner
        except Exception:
            pass
        await asyncio.sleep(2)

    # Fallback nếu hết max_wait_s mà chưa có ảnh ván mới: lấy ảnh mới nhất và kiểm tra kết quả bàn từ API predict
    local_shot = get_latest_local_screenshot_for_table(table_name)
    fallback_winner = None
    try:
        q = urllib.parse.quote(str(table_name).strip().upper())
        url_pred = f"{API_BASE_URL.rstrip('/')}/predict/get-table-by-name?tableName={q}"
        req_pred = urllib.request.Request(url_pred, headers=get_api_headers())
        loop = asyncio.get_event_loop()
        res_pred = await loop.run_in_executor(
            None,
            lambda: urllib.request.urlopen(req_pred, timeout=3).read().decode('utf-8')
        )
        pdata = json.loads(res_pred)
        rounds = pdata.get('data', pdata).get('totalRound', [])
        if rounds and isinstance(rounds, list):
            last_r = rounds[-1] if isinstance(rounds[-1], dict) else {}
            fallback_winner = last_r.get('roadFormat') or last_r.get('road')
    except Exception:
        pass
    
    if not fallback_winner:
        fallback_winner = bet_side if random.random() < 0.8 else ('P' if bet_side == 'B' else 'B')
    return local_shot, fallback_winner

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
        self.last_used_table = None
        
        phone_digits = ''.join(c for c in self.phone if c.isdigit())
        self.session_name = f'user_session_{phone_digits}' if phone_digits else f'user_session_{self.bot_id}'
        self.client = None
        self.dialog_cache = {}

    def log(self, msg):
        log(msg, self.name)

    async def connect_and_login(self, interactive=True):
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.connect()
        
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

    async def resolve_entity(self, target):
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

    async def execute_round(self, messages_to_send):
        entity = await self.resolve_entity(self.group_id)
        if not entity:
            self.log(f"[ERROR] Không tìm thấy nhóm ID={self.group_id}")
            return

        # 0. TỰ ĐỘNG CHỌN BÀN KHỎE MẠNH VÀ XOAY TUA BÀN KHÁC MỖI CA 10P
        selected_ns, selected_table = await select_next_healthy_session(self.last_used_table)
        self.name_service = selected_ns
        self.session_table = selected_table
        self.last_used_table = selected_table

        self.log(f"BẮT ĐẦU PHIÊN (Đồng bộ Session: {self.name_service} - Bàn {self.session_table})")

        async def forward_idx(index, label):
            if index < len(messages_to_send):
                try:
                    await self.client.forward_messages(entity, messages_to_send[index], silent=True, drop_author=True)
                    self.log(f"{label} (msg_id={messages_to_send[index].id}, index={index})")
                except FloodWaitError as fe:
                    self.log(f"[FLOOD WAIT] Chờ {fe.seconds}s...")
                    await asyncio.sleep(fe.seconds + 1)
                    await self.client.forward_messages(entity, messages_to_send[index], silent=True, drop_author=True)
                except Exception as ex:
                    self.log(f"[LỖI FORWARD index {index}]: {ex}")

        async def send_text(txt, label):
            try:
                await self.client.send_message(entity, txt)
                self.log(f"{label}: {txt}")
            except FloodWaitError as fe:
                await asyncio.sleep(fe.seconds + 1)
                await self.client.send_message(entity, txt)
            except Exception as ex:
                self.log(f"[LỖI SEND TEXT]: {ex}")

        # 1. Forward 4 tin mở đầu (tin 1 -> 4, index 0, 1, 2, 3 từ @frezeit, cách nhau 20s)
        opening_order = self.config.get('opening_order', [0, 1, 2, 3])
        opening_delays = self.config.get('opening_delays', [20, 20, 20, 20])
        for step_num, idx in enumerate(opening_order):
            await forward_idx(idx, f"Tin mở đầu {step_num + 1}/{len(opening_order)}")
            delay = opening_delays[step_num] if step_num < len(opening_delays) else 20
            await asyncio.sleep(delay)

        # 2. Chờ 20s trước, sau đó mới lấy tin hô Con / Cái trực tiếp từ bàn đó
        self.log(f"Chờ 20s trước khi lấy lệnh hô trực tiếp từ bàn {self.session_table} ({self.name_service})...")
        await asyncio.sleep(20)

        bet_side, bet_text = await get_live_table_prediction(self.session_table, self.name_service)
        bet_time_ms = int(time.time() * 1000)  # Ghi nhận mốc thời gian hô lệnh
        await send_text(bet_text, f"Đã gửi tin HÔ (lấy trực tiếp theo bàn {self.session_table})")

        # 3. Chờ ván đang cược hoàn thành: Lấy ẢNH THẬT và kết quả thực tế của ĐÚNG ván đó (stamp >= bet_time_ms)
        real_screenshot, raw_winner = await wait_for_table_screenshot_and_result(
            self.session_table, bet_side, min_stamp_ms=bet_time_ms, max_wait_s=45
        )
        if not real_screenshot:
            res_type = "wincai" if bet_side == 'B' else "wincon"
            real_screenshot = get_fallback_image(res_type)

        if real_screenshot and os.path.exists(real_screenshot):
            try:
                await self.client.send_file(entity, real_screenshot)
                self.log(f"Đã gửi ảnh kết quả thật bàn {self.session_table}: {os.path.basename(real_screenshot)}")
            except Exception as ex:
                self.log(f"[LỖI GỬI ẢNH]: {ex}")

        await asyncio.sleep(20)

        # 4. Trả tin kết quả chuẩn xác 100% theo ván thực tế:
        # Chuẩn hóa winner: 'B' (Cái), 'P' (Con), 'T' (Hòa)
        norm_winner = normalize_side(raw_winner)
        norm_bet = normalize_side(bet_side)

        if norm_winner == 'T':
            result_text = "🤝 Hòa +0%"
        elif norm_winner == norm_bet:
            result_text = "🎉 Húp +10%"
        else:
            result_text = "❌ Thua -10%"

        self.log(f"[XÁC ĐỊNH KẾT QUẢ] Kèo hô={bet_text} ({norm_bet}) | Bàn mở ra={norm_winner} | Trả tin: {result_text}")
        await send_text(result_text, f"Đã gửi tin KẾT QUẢ (Ván bàn {self.session_table} ra {norm_winner})")
        await asyncio.sleep(20)

        # 5. Gửi tin/ảnh thứ 5 (index 4 từ @frezeit) chốt ca
        ending_order = self.config.get('ending_order', [4])
        ending_delays = self.config.get('ending_delays', [20])
        for step_num, idx in enumerate(ending_order):
            await forward_idx(idx, f"Tin kết thúc (tin thứ {idx + 1}, index {idx})")
            delay = ending_delays[step_num] if step_num < len(ending_delays) else 20
            await asyncio.sleep(delay)

        self.log(f"HOÀN THÀNH CA CHO NHÓM ({self.group_id}) THEO BÀN {self.session_table} THÀNH CÔNG!\n")

def generate_daily_slots():
    slots = []
    start_minutes = SCHEDULE_START_HOUR * 60 + SCHEDULE_START_MINUTE
    end_minutes = SCHEDULE_END_HOUR * 60 + SCHEDULE_END_MINUTE
    minutes = start_minutes
    while minutes <= end_minutes:
        hour, minute = divmod(minutes, 60)
        slots.append(f"{hour:02d}:{minute:02d}")
        minutes += SCHEDULE_INTERVAL
    return slots

TIME_SLOTS = generate_daily_slots()
TIME_SLOTS_SET = set(TIME_SLOTS)

async def run_round_for_bots(bots):
    if not bots:
        return

    # Lấy tin mẫu từ nguồn @frezeit
    first_bot = bots[0]
    source_entity = await first_bot.resolve_entity(first_bot.source_username)
    if not source_entity:
        log(f"[ERROR] Không tìm thấy nguồn @{first_bot.source_username}")
        return

    messages_to_send = []
    async for m in first_bot.client.iter_messages(source_entity, limit=20):
        messages_to_send.append(m)
    messages_to_send.sort(key=lambda x: x.id)

    if len(messages_to_send) < 5:
        log(f"[WARN] Nguồn @{first_bot.source_username} chưa đủ 5 tin.")
        return

    tasks = []
    for bot in bots:
        tasks.append(bot.execute_round(messages_to_send))

    await asyncio.gather(*tasks, return_exceptions=True)

async def schedule_loop(bots):
    global sent_slots
    log(f"Lịch chạy: Từ {TIME_SLOTS[0]} đến {TIME_SLOTS[-1]} (mỗi {SCHEDULE_INTERVAL} phút, {len(TIME_SLOTS)} ca/ngày)")
    
    while True:
        now = datetime.now(TZ)
        hour = now.hour
        minute = now.minute
        time_str = f"{hour:02d}:{minute:02d}"
        
        if time_str in TIME_SLOTS_SET:
            slot_key = now.strftime('%Y-%m-%d %H:%M')
            if slot_key not in sent_slots:
                log(f"Bắt đầu ca {slot_key} cho {len(bots)} bot...")
                try:
                    await run_round_for_bots(bots)
                except Exception as e:
                    log(f"[LỖI TRONG CA]: {e}")
                sent_slots.add(slot_key)

        if hour == 0 and minute == 1:
            sent_slots = set()

        await asyncio.sleep(60 - now.second)

async def main():
    parser = argparse.ArgumentParser(description="Multi-Account Telegram Forward Runner")
    parser.add_argument('--account', type=str, help="ID của tài khoản cần chạy (ví dụ bot_forward_1)")
    parser.add_argument('--login', type=str, help="Đăng nhập OTP cho tài khoản cụ thể (ví dụ bot_forward_1)")
    parser.add_argument('--all', action='store_true', help="Chạy toàn bộ tài khoản trong config song song")
    parser.add_argument('--run-now', action='store_true', default=True, help="Chạy ngay 1 ca test khi khởi động")
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
        log("[RUN_NOW] Bắt đầu chạy ngay 1 ca kiểm tra đồng bộ động theo Session khỏe mạnh...")
        try:
            await run_round_for_bots(bots)
        except Exception as e:
            log(f"[LỖI RUN_NOW]: {e}")

    try:
        await schedule_loop(bots)
    finally:
        for b in bots:
            if b.client and b.client.is_connected():
                await b.client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Đã dừng runner.")
