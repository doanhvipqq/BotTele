import requests
import urllib.parse
import json
import time
from telebot import types

# Headers giả lập
HEADERS = {
    "accept": "*/*",
    "accept-language": "vi",
    "user-agent": "Mozilla/5.0"
}

def register_mmo(bot):
    @bot.message_handler(commands=['4mmo'])
    def handle_4mmo_command(message):
        # Lấy tham số (URL) từ tin nhắn
        try:
            command_parts = message.text.split()
            if len(command_parts) < 2:
                bot.reply_to(message, "⚠️ Vui lòng nhập link.\nVí dụ: /4mmo https://google.com/")
                return
            
            web = command_parts[1].strip()
        except:
            bot.reply_to(message, "⚠️ Lỗi cú pháp. Ví dụ: /4mmo https://google.com/")
            return

        if not web.endswith("/"):
            web += "/"

        # Gửi tin nhắn ban đầu
        sent_msg = bot.reply_to(message, "⏳ Đang kết nối tới 4mmo...")
        chat_id = message.chat.id
        message_id = sent_msg.message_id

        try:
            # Bước 1: Request khởi tạo
            requests.get("https://4mmo.net/cd?&t=1", headers=HEADERS)
            
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⏳ Đang đợi server phản hồi (3s)...")
            time.sleep(3)

            # Bước 2: Tạo URL load traffic
            encoded_web = urllib.parse.quote(web, safe='')
            url2 = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={encoded_web}&t=1"

            retry_count = 0
            max_retries = 30 

            while retry_count < max_retries:
                res2 = requests.get(url2, headers=HEADERS)
                text2 = res2.text

                try:
                    j = json.loads(text2)
                except:
                    time.sleep(2)
                    retry_count += 1
                    continue

                # Trường hợp 1: Có mã
                if j.get("status") == 1 and j.get("data", {}).get("html"):
                    code = j["data"]["html"]
                    bot.edit_message_text(
                        chat_id=chat_id, 
                        message_id=message_id, 
                        text=f"✅ **Lấy mã thành công!**\n\n🌐 Web: {web}\n🔑 Code: `{code}`",
                        parse_mode="Markdown"
                    )
                    return

                # Trường hợp 2: Đang chờ (#5)
                if j.get("status") == 0 and "#5" in j.get("message", ""):
                    if retry_count % 3 == 0: # Cập nhật tin nhắn mỗi 3 lần lặp để đỡ spam
                        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"⏳ Đang chờ mã... (Lần thử {retry_count})")
                    time.sleep(2)
                    retry_count += 1
                    continue
                
                # Trường hợp 3: Sai web
                if j.get("status") == 0 and "#1" in j.get("message", ""):
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ Sai web lấy mã, vui lòng kiểm tra lại!")
                    return
                
                retry_count += 1
                time.sleep(2)

            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ Quá thời gian chờ (timeout).")

        except Exception as e:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ Lỗi: {str(e)}")
