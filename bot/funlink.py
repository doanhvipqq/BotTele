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
            bot.edit_message_text(f"❌ Thất bại bước 2: {response.status_code}", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Lỗi gửi request bước 2: {e}", message.chat.id, wait_msg.message_id)


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
            "⏳ Đang dò nhiệm vụ hỗ trợ cho link `{link_id}`...",
            reply_to_message_id=message.message_id
        )

        # Lặp đến khi nhiệm vụ hợp lệ
        retry = 0
        max_retry = 20
        keyword = ""
        keyword_id = ""

        while retry < max_retry:
            retry += 1
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
                    keyword = j['data_keyword']['keyword_text'].lower()
                    keyword_id = j['data_keyword']['id']
                    if keyword in SOURCES:
                        break
                    else:
                        bot.edit_message_text(
                            f"⏳ Nhiệm vụ hiện tại chưa hỗ trợ: `{keyword}`\nĐang thử lại... (lần {retry})",
                            message.chat.id,
                            wait_msg.message_id,
                            parse_mode="Markdown"
                        )
                else:
                    bot.edit_message_text(f"❌ Không lấy được nhiệm vụ. Thử lại... ({r.status_code})",
                                          message.chat.id, wait_msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"⚠️ Lỗi trong lúc lấy nhiệm vụ: {e}",
                                      message.chat.id, wait_msg.message_id)
            time.sleep(3)


        if keyword not in SOURCES:
            bot.edit_message_text(
                f"🚫 Sau {max_retry} lần thử, nhiệm vụ vẫn chưa được hỗ trợ.\nLoại nhận được: `{keyword}`",
                message.chat.id,
                wait_msg.message_id,
                parse_mode="Markdown"
            )
            return

        # fresponse = requests.options('https://public.funlink.io/api/code/ch', headers=headers)
        # if fresponse.status_code != 200:
        #     bot.edit_message_text(f"❌ Thất bại bước 1: {fresponse.status_code}", message.chat.id, wait_msg.message_id)
        #     return
            
        # threading.Thread(
        #     target=process_funlink_step,
        #     args=(bot, message, wait_msg, origin, headers),
        #     daemon=True
        # ).start()


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

        bot.edit_message_text(
            f"✅ Đã tìm thấy nhiệm vụ `{keyword}`.\n⏳ Đang gửi yêu cầu bước 1...",
            message.chat.id,
            wait_msg.message_id,
            parse_mode="Markdown"
        )

        fresponse = requests.options('https://public.funlink.io/api/code/ch', headers=headers)
        if fresponse.status_code != 200:
            bot.edit_message_text(f"❌ Thất bại bước 1: {fresponse.status_code}", message.chat.id, wait_msg.message_id)
            return

        threading.Thread(
            target=process_funlink_step,
            args=(bot, message, wait_msg, origin, headers),
            daemon=True
        ).start()
