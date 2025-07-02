import re
import time
import random
import requests
import threading
from telebot.types import Message

SOURCES = {
    '188bet': 'https://88bet.hiphop',
    'w88': 'https://w88vt.com',
    'fun88': 'https://fun88kyc.com',
    'daga': 'https://stelizabeth.co.uk',
    'kubet': 'https://www.randalls.uk.com',
    '8xbet 8xbetvina.com': 'https://8xbetvina.com',
    'trang cá cược': 'https://chisholmunitedfc.com',
    'lu88 vnco': 'https://lu88vn.co.uk',
    'm88lu': 'https://m88lu.io',
}

def process_funlink_step(bot, message, wait_msg, origin, headers):
    for remaining in range(60, 0, -5):
        try:
            bot.edit_message_text(
                f"⏳ Đang xử lý... vui lòng chờ {remaining} giây.",
                message.chat.id,
                wait_msg.message_id
            )
        except:
            pass
        time.sleep(5)

    headers['content-type'] = 'application/json'
    json_data = {
        'screen': '1000 x 800',
        'browser_name': 'Safari',
        'browser_version': '100.0.0.0',
        'browser_major_version': '137',
        'is_mobile': False,
        'os_name': 'skibidiOS',
        'os_version': '10000000',
        'is_cookies': True,
        'href': origin + '/',
        'user_agent': headers['user-agent'],
        'hostname': origin,
    }

    try:
        # Bước 2: lấy mã code
        response = requests.post('https://public.funlink.io/api/code/code', headers=headers, json=json_data)
        if response.status_code != 200:
            bot.edit_message_text(f"❌ Bước 2 thất bại ({response.status_code})", message.chat.id, wait_msg.message_id)
            return

        code = response.json().get('code')
        if not code:
            bot.edit_message_text(
                f"⚠️ Không tìm thấy mã code trong phản hồi.",
                message.chat.id,
                wait_msg.message_id,
            )
            return

        # Bước 3: gửi mã lấy link đích
        json_verify = {
            'code': code,
            'hostname': origin,
            'user_agent': headers['user-agent']
        }

        verify_res = requests.post('https://public.funlink.io/api/code/verify', headers=headers, json=json_verify)
        if verify_res.status_code != 200:
            bot.edit_message_text(f"❌ Bước 3 thất bại ({verify_res.status_code})", message.chat.id, wait_msg.message_id)
            return

        final_url = verify_res.json().get('url')
        if final_url:
            bot.edit_message_text(
                f"🎯 <b>Link đích:</b> <code>{final_url}</code>",
                message.chat.id,
                wait_msg.message_id,
            )

        else:
            bot.edit_message_text("❌ Không lấy được link đích.", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ Lỗi xử lý: {e}", message.chat.id, wait_msg.message_id)

def register_funlink(bot):
    @bot.message_handler(commands=['fl'])
    def handle_get_code(message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng nhập link Funlink cần vượt.\nVí dụ: /fl https://funlink.io/PS3HIRn")
            return

        url = args[1].strip().lower()
        match = re.search(r'funlink\.io/([a-zA-Z0-9]+)', url)
        if not match:
            bot.reply_to(message, "🚫 Link không hợp lệ.")
            return

        link_id = match.group(1)
        rad = str(random.randint(100000, 999999))
        
        # Gửi tin nhắn ban đầu
        wait_msg = bot.send_message(
            message.chat.id,
            "⏳ Đang xử lý, vui lòng chờ...",
            reply_to_message_id=message.message_id
        )

        # Dò keyword đến khi hợp lệ
        retry = 0
        keyword = ""
        while retry < 20:
            try:
                r = requests.get(
                    'https://public.funlink.io/api/code/renew-key',
                    params={'ignoreId': rad, 'id': link_id},
                    headers={
                        'accept': '*/*',
                        'origin': 'https://funlink.io',
                        'referer': 'https://funlink.io/',
                        'rid': rad,
                        'user-agent': 'Mozilla/5.0'
                    },
                    timeout=10
                )
                if r.status_code == 200:
                    j = r.json()
                    keyword = r.json().get('data_keyword', {}).get('keyword_text', '').lower()
                    if keyword in SOURCES:
                        break
                    
            except Exception:
                pass
            retry += 1
            time.sleep(2)

        if keyword not in SOURCES:
            bot.edit_message_text(
                f"🚫 Không tìm thấy nhiệm vụ được hỗ trợ.",
                message.chat.id,
                wait_msg.message_id,
            )
            return

        origin = SOURCES[keyword]
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'origin': origin,
            'priority': 'u=1, i',
            'referer': origin + '/',
            'rid': rad,
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
        }

        # Gửi yêu cầu bước 1
        fresponse = requests.options('https://public.funlink.io/api/code/ch', headers=headers)
        if fresponse.status_code != 200:
            bot.edit_message_text(f"❌ Thất bại bước 1: {fresponse.status_code}", message.chat.id, wait_msg.message_id)
            return

        threading.Thread(
            target=process_funlink_step,
            args=(bot, message, wait_msg, origin, headers),
            daemon=True
        ).start()
