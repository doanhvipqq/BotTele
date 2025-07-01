import re
import time
import random
import threading
import requests
from telebot.types import Message

def process_funlink_step(bot, message, wait_msg, link_id, rad):
    try:
        # 1️⃣ Gọi API để lấy `code`, `keyword`, `keyword_id`
        params = {'ignoreId': rad, 'id': link_id}
        headers1 = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0',
            'origin': 'https://funlink.io',
            'referer': 'https://funlink.io/',
            'rid': rad,
        }
        resp = requests.get('https://public.funlink.io/api/code/renew-key', headers=headers1, params=params)
        if resp.status_code != 200:
            bot.edit_message_text(f"❌ Bước 1 lỗi: mã {resp.status_code}", message.chat.id, wait_msg.message_id)
            return
        dat = resp.json()
        code = dat.get('code')
        keyword = dat.get('data_keyword', {}).get('keyword_text')
        kw_id = dat.get('data_keyword', {}).get('id')
        if not (code and keyword and kw_id):
            bot.edit_message_text("❌ Thiếu dữ liệu `code`/`keyword`", message.chat.id, wait_msg.message_id)
            return

        # 2️⃣ Gửi OPTIONS (chuẩn bị)
        origin = f"https://{keyword.lower()}.com"  # hoặc cấu hình map nếu domain khác
        headers_opt = dict(headers1, origin=origin, referer=origin + '/')
        op = requests.options('https://public.funlink.io/api/code/ch', headers=headers_opt)
        if op.status_code != 200:
            bot.edit_message_text(f"❌ OPTIONS lỗi: mã {op.status_code}", message.chat.id, wait_msg.message_id)
            return

        # 3️⃣ Đếm ngược 60 giây
        for rem in range(60, 0, -5):
            bot.edit_message_text(f"⏳ Đợi {rem} giây...", message.chat.id, wait_msg.message_id)
            time.sleep(5)

        # 4️⃣ Gửi POST để lấy mã
        json_post = {
            'screen': '1000 x 800',
            'browser_name': 'Safari',
            'browser_version': '100.0.0.0',
            'browser_major_version': '137',
            'is_mobile': False,
            'os_name': 'skibidiOS',
            'os_version': '10000000',
            'is_cookies': True,
            'href': origin + '/',
            'user_agent': headers1['user-agent'],
            'hostname': origin,
        }
        headers_post = dict(headers_opt, **{'content-type': 'application/json'})
        p = requests.post('https://public.funlink.io/api/code/code', headers=headers_post, json=json_post)
        if p.status_code != 200:
            bot.edit_message_text(f"❌ POST step2 lỗi: mã {p.status_code}", message.chat.id, wait_msg.message_id)
            return

        # 5️⃣ Gửi POST để lấy link đích
        payload2 = {
            'browser_name': 'skibidu',
            'browser_version': '99999',
            'os_name': 'SkibidiOS',
            'os_version': '10000',
            'os_version_name': '1000',
            'keyword_answer': code,
            'link_shorten_id': link_id,
            'keyword': keyword,
            'ip': '',
            'user_agent': headers1['user-agent'],
            'device_name': 'desktop',
            'token': '',
            'keyword_id': kw_id,
        }
        headers2 = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'origin': 'https://funlink.io',
            'referer': 'https://funlink.io/',
            'rid': rad,
            'user-agent': headers1['user-agent']
        }
        final = requests.post('https://public.funlink.io/api/url/tracking-url', headers=headers2, json=payload2)
        if final.status_code == 200 and final.json().get('data_link', {}).get('url'):
            final_url = final.json()['data_link']['url']
            bot.edit_message_text(f"✅ Link đích:\n<code>{final_url}</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(f"❌ Lấy link đích lỗi: mã {final.status_code}", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Lỗi: {e}", message.chat.id, wait_msg.message_id)

def register_funlink(bot):
    @bot.message_handler(commands=['fl'])
    def handle_funlink(message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng nhập URL như /fl https://funlink.io/abc123")
            return

        url = args[1].strip()
        m = re.search(r"funlink\.io/([A-Za-z0-9]+)", url)
        if not m:
            bot.reply_to(message, "❌ Không đúng định dạng URL funlink.io")
            return

        link_id = m.group(1)
        rad = str(random.randint(100000, 999999))
        wait = bot.reply_to(message, "⏳ Bắt đầu xử lý...")

        threading.Thread(target=process_funlink_step, args=(bot, message, wait, link_id, rad), daemon=True).start()