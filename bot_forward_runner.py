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

def get_latest_local_screenshot():
    if not os.path.exists(SCREENSHOT_DIR):
        return None
    try:
        files = [
            os.path.join(SCREENSHOT_DIR, f)
            for f in os.listdir(SCREENSHOT_DIR)
            if f.lower().endswith(IMAGE_EXTENSIONS) and not f.startswith('.')
        ]
        if not files:
            return None
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for f in files[:5]:
            if is_real_screenshot_file(f):
                return f
    except Exception:
        pass
    return None

async def get_real_screenshot(api_url=API_BASE_URL):
    if api_url:
        try:
            url = f"{api_url.rstrip('/')}/api/latest-screenshot"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            loop = asyncio.get_event_loop()
            res_text = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(req, timeout=3).read().decode('utf-8')
            )
            res_data = json.loads(res_text)
            if res_data.get('success') and res_data.get('data'):
                filepath = res_data['data'].get('filepath')
                if filepath and os.path.exists(filepath) and is_real_screenshot_file(filepath):
                    return filepath
        except Exception:
            pass

    return get_latest_local_screenshot()

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
        self.source_username = config.get('source_username', 'frezeit')
        
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

    async def execute_round(self, messages_to_send, round_outcome, real_screenshot_path):
        entity = await self.resolve_entity(self.group_id)
        if not entity:
            self.log(f"[ERROR] Không tìm thấy nhóm ID={self.group_id}")
            return

        self.log(f"BẮT ĐẦU PHIÊN CHO NHÓM: {getattr(entity, 'title', self.group_id)}")

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

        # 1. Forward tin 1 -> 4 (index 0, 1, 2, 3)
        opening_order = self.config.get('opening_order', [0, 1, 2, 3])
        opening_delays = self.config.get('opening_delays', [5, 5, 5, 5])
        for step_num, idx in enumerate(opening_order):
            await forward_idx(idx, f"Tin mở đầu {step_num + 1}/{len(opening_order)}")
            delay = opening_delays[step_num] if step_num < len(opening_delays) else 5
            await asyncio.sleep(delay)

        # 2. Hô cược: 🔵 CON hoặc 🔴 CÁI
        await send_text(round_outcome['bet_text'], "Đã gửi tin HÔ")
        await asyncio.sleep(15)

        # 3. Gửi ảnh kết quả
        if real_screenshot_path and os.path.exists(real_screenshot_path):
            try:
                await self.client.send_file(entity, real_screenshot_path)
                self.log(f"Đã gửi ảnh kết quả thật: {os.path.basename(real_screenshot_path)}")
            except Exception as ex:
                self.log(f"[LỖI GỬI ẢNH]: {ex}")

        await asyncio.sleep(5)

        # 4. Gửi kết quả: 🎉 Húp +10% / ❌ Thua -10% / 🤝 Hòa +0%
        await send_text(round_outcome['result_text'], "Đã gửi tin KẾT QUẢ")
        await asyncio.sleep(10)

        # 5. Gửi tin/ảnh thứ 5 (index 4)
        ending_order = self.config.get('ending_order', [4])
        ending_delays = self.config.get('ending_delays', [5])
        for step_num, idx in enumerate(ending_order):
            await forward_idx(idx, f"Tin kết thúc (tin thứ {idx + 1}, index {idx})")
            delay = ending_delays[step_num] if step_num < len(ending_delays) else 5
            await asyncio.sleep(delay)

        self.log(f"HOÀN THÀNH PHIÊN CHO NHÓM ({self.group_id}) THÀNH CÔNG!\n")

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

    # Lấy tin mẫu từ nguồn của bot đầu tiên (hoặc frezeit)
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

    # Sinh cược và kết quả chung
    is_cai = random.choice([True, False])
    bet_text = "🔴 CÁI" if is_cai else "🔵 CON"

    rand_res = random.random()
    if rand_res < 0.70:
        is_win, is_tie = True, False
        res_text = "🎉 Húp +10%"
        res_type = "wincai" if is_cai else "wincon"
    elif rand_res < 0.95:
        is_win, is_tie = False, False
        res_text = "❌ Thua -10%"
        res_type = "losecai" if is_cai else "losecon"
    else:
        is_win, is_tie = False, True
        res_text = "🤝 Hòa +0%"
        res_type = "tie"

    round_outcome = {
        'is_cai': is_cai,
        'is_win': is_win,
        'is_tie': is_tie,
        'bet_text': bet_text,
        'result_text': res_text,
        'result_type': res_type
    }

    # Lấy ảnh thật từ session
    real_screenshot = await get_real_screenshot()
    if not real_screenshot:
        real_screenshot = get_fallback_image(res_type)

    tasks = []
    for idx, bot in enumerate(bots):
        tasks.append(bot.execute_round(messages_to_send, round_outcome, real_screenshot))

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

    log(f"=== KHỞI ĐỘNG HỆ THỐNG FORWARD VỚI {len(target_accounts)} TÀI KHOẢN ===")
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
        log("[RUN_NOW] Bắt đầu chạy ngay 1 ca kiểm tra cho tất cả các bot...")
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
