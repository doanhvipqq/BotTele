import re
import time
import random
import requests
import threading
from telebot.types import Message

def register_funlink(bot):
    @bot.message_handler(commands=['fl'])
    def handle_funlink(message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng nhập URL funlink.io\nVí dụ: <code>/fl https://funlink.io/abc123</code>", parse_mode="HTML")
            return

        url = args[1].strip()
        url_match = re.search(r"funlink\.io/([A-Za-z0-9]+)", url)
        if not url_match:
            bot.reply_to(message, "❌ Không tìm thấy ID từ liên kết funlink.io.")
            return

        link_id = url_match.group(1)
        rad = str(random.randint(100000, 999999))

        headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
            'origin': 'https://funlink.io',
            'referer': 'https://funlink.io/',
            'rid': rad
        }
        params = {'ignoreId': rad, 'id': link_id}

        wait_msg = bot.reply_to(message, "⏳ Đang gửi yêu cầu bước 1...")

        resp = requests.get('https://public.funlink.io/api/code/renew-key', headers=headers, params=params)
        if resp.status_code != 200:
            bot.edit_message_text(f"❌ Không lấy được thông tin từ funlink.io (mã {resp.status_code})", message.chat.id, wait_msg.message_id)
            return

        try:
            dat = resp.json()
            keyword = dat['data_keyword']['keyword_text']
            keyword_id = dat['data_keyword']['id']
            code = dat['code']
        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi phân tích dữ liệu: {e}", message.chat.id, wait_msg.message_id)
            return

        # Gửi yêu cầu OPTIONS (bước chuẩn bị)
        ORIGIN_MAP = {
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

        origin = ORIGIN_MAP.get(keyword.lower())
        if not origin:
            bot.edit_message_text(f"⚠️ Từ khóa <b>{keyword}</b> chưa được hỗ trợ để lấy link đích.", message.chat.id, wait_msg.message_id, parse_mode="HTML")
            return

        # Gửi OPTIONS
        fheaders = {
            **headers,
            'origin': origin,
            'referer': origin + '/'
        }
        options = requests.options('https://public.funlink.io/api/code/ch', headers=fheaders)
        if options.status_code != 200:
            bot.edit_message_text(f"❌ Thất bại bước OPTIONS (mã {options.status_code})", message.chat.id, wait_msg.message_id)
            return

        # Bắt đầu đếm ngược
        def countdown_and_send():
            try:
                for remaining in range(60, 0, -5):
                    bot.edit_message_text(f"⏳ Đang xử lý... vui lòng chờ {remaining} giây.", message.chat.id, wait_msg.message_id)
                    time.sleep(5)

                # Chuẩn bị dữ liệu POST
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

                fheaders['content-type'] = 'application/json'
                post = requests.post('https://public.funlink.io/api/code/code', headers=fheaders, json=json_data)
                if post.status_code != 200:
                    bot.edit_message_text(f"❌ Thất bại POST step 2 (mã {post.status_code})", message.chat.id, wait_msg.message_id)
                    return

                # Chuẩn bị bước cuối: lấy link đích
                payload = {
                    'browser_name': 'skibidu',
                    'browser_version': '99999',
                    'os_name': 'SkibidiOS',
                    'os_version': '10000',
                    'os_version_name': '1000',
                    'keyword_answer': code,
                    'link_shorten_id': link_id,
                    'keyword': keyword,
                    'ip': '',
                    'user_agent': headers['user-agent'],
                    'device_name': 'desktop',
                    'token': '',
                    'keyword_id': keyword_id,
                }
                final_headers = {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    'origin': 'https://funlink.io',
                    'referer': 'https://funlink.io/',
                    'rid': rad,
                    'user-agent': headers['user-agent']
                }
                final = requests.post('https://public.funlink.io/api/url/tracking-url', headers=final_headers, json=payload)
                if final.status_code == 200:
                    final_link = final.json()['data_link']['url']
                    bot.edit_message_text(f"✅ Link đích của bạn là:\n<code>{final_link}</code>", message.chat.id, wait_msg.message_id, parse_mode="HTML")
                else:
                    bot.edit_message_text(f"❌ Không lấy được link đích (mã {final.status_code})", message.chat.id, wait_msg.message_id)

            except Exception as e:
                bot.edit_message_text(f"❌ Lỗi xử lý: {e}", message.chat.id, wait_msg.message_id)

        # Chạy countdown trong thread riêng
        threading.Thread(target=countdown_and_send, daemon=True).start()