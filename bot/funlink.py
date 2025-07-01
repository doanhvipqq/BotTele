import time
import random
import requests
from telebot.types import Message

SOURCES = {
    '188bet': 'https://88bet.hiphop',
    'w88': 'https://w88vt.com',
    'fun88': 'https://fun88kyc.com',
    'daga': 'https://stelizabeth.co.uk',
}

def register_funlink(bot):
    @bot.message_handler(commands=['fl'])
    def handle_get_code(message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng nhập từ khoá muốn lấy mã.\nVí dụ: /fl 188bet")
            return

        key = args[1].strip().lower()
        origin = SOURCES.get(key)
        if not origin:
            bot.reply_to(message, "🚫 Từ khoá này hiện chưa hỗ trợ.\nCác từ khoá đang hỗ trợ gồm: 188bet, w88, fun88, daga")
            return

        rad = str(random.randint(100000, 999999))
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

        # Gửi tin nhắn ban đầu
        wait_msg = bot.send_message(
            message.chat.id,
            "⏳ Đang gửi yêu cầu bước 1...",
            reply_to_message_id=message.message_id
        )

        fresponse = requests.options('https://public.funlink.io/api/code/ch', headers=headers)
        if fresponse.status_code != 200:
            bot.edit_message_text(f"❌ Thất bại bước 1: {fresponse.status_code}", message.chat.id, wait_msg.message_id)
            return

        # Đếm ngược 60 giây, mỗi 5 giây cập nhật
        for remaining in range(60, 0, -5):
            bot.edit_message_text(
                f"⏳ Đang xử lý... vui lòng chờ {remaining} giây.",
                message.chat.id,
                wait_msg.message_id
            )
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

        response = requests.post('https://public.funlink.io/api/code/code', headers=headers, json=json_data)
        if response.status_code == 200:
            try:
                dat = response.json()
                code = dat.get('code')
                if code:
                    bot.edit_message_text(
                        f" » <b>Mã của bạn là:</b> <blockquote>{code}</blockquote>\n🎉 Hãy nhập mã để lấy link đích.",
                        message.chat.id,
                        wait_msg.message_id,
                    )
                else:
                    bot.edit_message_text("❌ Không tìm thấy mã trong phản hồi.", message.chat.id, wait_msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Lỗi xử lý JSON: {e}", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(
                f"❌ Thất bại bước 2: {response.status_code}",
                message.chat.id, wait_msg.message_id
            )
