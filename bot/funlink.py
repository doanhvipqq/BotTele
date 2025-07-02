import re
import time
import random
import requests
import threading

def register_funlink(bot):
    @bot.message_handler(commands=['fl'])
    def handle_fl(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❗ Vui lòng nhập link Funlink. Ví dụ:\n`/fl https://funlink.io/PS3HIRn`", parse_mode="Markdown")
            return

        nurl = args[1].strip()
        sent_msg = bot.send_message(
            message.chat.id,
            "⏳ Đang xử lý nhiệm vụ... Vui lòng chờ ~60 giây.",
            reply_to_message_id=message.message_id
        )

        # 👇 Khởi chạy bypass trong luồng riêng
        threading.Thread(
            target=process_bypass,
            args=(bot, nurl, sent_msg),
            daemon=True
        ).start()

    def process_bypass(bot, nurl, sent_msg):
        try:
            result = bypass_funlink(nurl)
            bot.edit_message_text(result, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"⚠️ Lỗi: {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

    def bypass_funlink(nurl):
        rod = random.randint(100000, 999999)
        rad = str(rod)

        urlmatch = re.search(r"funlink\.io/([A-Za-z0-9]+)", nurl)
        if not urlmatch:
            return "❌ Link không hợp lệ."

        link_id = urlmatch.group(1)

        # Tùy theo loại nhiệm vụ mà origin & href khác nhau
        DOMAIN_MAP = {
            '188Bet': 'https://88bet.hiphop',
            'w88': 'https://w88vt.com',
            'fun88': 'https://fun88kyc.com',
            'daga': 'https://stelizabeth.co.uk',
            'kubet': 'https://www.randalls.uk.com',
            '8xbet 8xbetvina.com': 'https://8xbetvina.com',
            'trang cá cược': 'https://chisholmunitedfc.com',
            'lu88 vnco': 'https://lu88vn.co.uk',
            'm88lu': 'https://m88lu.io',
        }

        headers = {
            'accept': '*/*',
            'origin': 'https://funlink.io',
            'referer': 'https://funlink.io/',
            'rid': rad,
            'user-agent': 'Mozilla/5.0',
        }

        params = {
            'ignoreId': rad,
            'id': link_id,
        }

        # 🔁 Lặp lại tối đa 10 lần để thử lấy nhiệm vụ hợp lệ
        max_retry = 10
        for attempt in range(max_retry):
            r1 = requests.get('https://public.funlink.io/api/code/renew-key', params=params, headers=headers)
            if r1.status_code != 200:
                return "❌ Không lấy được keyword."

            dt = r1.json()
            keyword = dt['data_keyword']['keyword_text']
            keyword_id = dt['data_keyword']['id']

            if keyword in DOMAIN_MAP:
                break  # ✅ Hợp lệ → thoát khỏi vòng lặp và xử lý tiếp
            else:
                time.sleep(3)  # ⏱ Đợi vài giây trước khi thử lại
        else:
            return f"⚠️ Đã thử {max_retry} lần nhưng không có nhiệm vụ được hỗ trợ."

        origin = DOMAIN_MAP[keyword]
        href_sample = f"{origin}/"

        # Bước 1: options
        fheaders = {
            'origin': origin,
            'referer': origin + '/',
            'rid': rad,
            'user-agent': 'Mozilla/5.0'
        }
        requests.options('https://public.funlink.io/api/code/ch', headers=fheaders)

        # Bước 2: chờ và gửi thông tin
        time.sleep(60)
        json_data = {
            'screen': '1000 x 800',
            'browser_name': 'Safari',
            'browser_version': '100.0.0.0',
            'browser_major_version': '137',
            'is_mobile': False,
            'os_name': 'skibidiOS',
            'os_version': '10000000',
            'is_cookies': True,
            'href': href_sample,
            'user_agent': 'Mozilla/5.0',
            'hostname': origin
        }

        r2 = requests.post('https://public.funlink.io/api/code/code', headers={
            'origin': origin,
            'referer': origin + '/',
            'rid': rad,
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0'
        }, json=json_data)

        if r2.status_code != 200:
            return f"❌ Bước 2 thất bại ({r2.status_code})"

        code_data = r2.json()
        final_code = code_data.get('code')

        if not final_code:
            return "❌ Không lấy được code."

        # Bước 3: gửi truy cập cuối để lấy link đích
        final_payload = {
            'browser_name': 'skibidu',
            'browser_version': '99999',
            'os_name': 'SkibidiOS',
            'os_version': '10000',
            'os_version_name': '1000',
            'keyword_answer': final_code,
            'link_shorten_id': link_id,
            'keyword': keyword,
            'ip': '',
            'user_agent': 'Mozilla/5.0',
            'device_name': 'desktop',
            'token': '',
            'keyword_id': keyword_id,
        }

        r3 = requests.post('https://public.funlink.io/api/url/tracking-url', headers={
            'accept': 'application/json',
            'content-type': 'application/json',
            'origin': 'https://funlink.io',
            'referer': 'https://funlink.io/',
            'rid': rad,
            'user-agent': 'Mozilla/5.0',
        }, json=final_payload)

        if r3.status_code == 200:
            dtt = r3.json()
            return f"🔗 Link đích: {dtt['data_link']['url']}"
        return "❌ Không lấy được link cuối."
