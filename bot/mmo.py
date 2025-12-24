import requests
import urllib.parse
import json
import time
from telebot import types

# 1. HEADERS GỐC (Giống y hệt file 4mmo.py)
headers = {
    "accept": "*/*",
    "accept-language": "vi",
    "user-agent": "Mozilla/5.0"
}

def register_mmo(bot):
    @bot.message_handler(commands=['4mmo'])
    def handle_4mmo_command(message):
        # --- XỬ LÝ ĐẦU VÀO (Thay cho input) ---
        try:
            command_parts = message.text.split()
            if len(command_parts) < 2:
                bot.reply_to(message, "⚠️ Nhập link. Ví dụ: /4mmo https://google.com/")
                return
            web = command_parts[1].strip()
        except:
            return

        # Logic gốc: Kiểm tra dấu / ở cuối
        if not web.endswith("/"):
            web += "/"

        # Gửi tin nhắn xác nhận đã nhận lệnh
        msg = bot.reply_to(message, "⏳ Đang chạy code gốc...")
        chat_id = message.chat.id
        msg_id = msg.message_id

        try:
            # --- BẮT ĐẦU LOGIC GỐC ---
            
            # Request 1: Kích hoạt (Giống dòng 19 file gốc)
            requests.get("https://4mmo.net/cd?&t=1", headers=headers)
            
            # Sleep 3s (Giống dòng 20 file gốc)
            time.sleep(3)

            # Tạo URL 2 (Giống dòng 22 file gốc)
            url2 = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={urllib.parse.quote(web, safe='')}&t=1"

            # Vòng lặp (Thay cho while True vô hạn, mình để 30 lần để tránh treo bot vĩnh viễn)
            count = 0
            while count < 40:
                # Request 2 (Giống dòng 25 file gốc)
                res2 = requests.get(url2, headers=headers)
                text2 = res2.text
                
                # In ra console để bạn check (Giống dòng 27 file gốc)
                print(f"Server trả về: {text2}")

                try:
                    j = json.loads(text2)
                except:
                    # Giống dòng 30-32 file gốc
                    time.sleep(2)
                    count += 1
                    continue

                # Trường hợp 1: Có mã (Giống dòng 34 file gốc)
                if j.get("status") == 1 and j.get("data", {}).get("html"):
                    code = j["data"]["html"]
                    # Thay print bằng edit_message
                    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"✅ Mã của bạn: `{code}`", parse_mode="Markdown")
                    break

                # Trường hợp 2: Đang chờ (Giống dòng 38 file gốc)
                if j.get("status") == 0 and "#5" in j.get("message", ""):
                    # Cập nhật tin nhắn để người dùng biết bot vẫn đang chạy
                    if count % 2 == 0:
                        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"⏳ Chưa có mã, đang thử lại.. ({count})")
                    
                    time.sleep(2)
                    count += 1
                    continue
                
                # Trường hợp 3: Sai web (Giống dòng 43 file gốc)
                if j.get("status") == 0 and "#1" in j.get("message", ""):
                    bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="❌ Sai web lấy mã, vui lòng kiểm tra lại!")
                    break

                # Nếu break ở file gốc (dòng 47) -> Break loop
                # Nhưng vì ta cần loop tiếp nếu chưa có mã, đoạn này giữ nguyên logic continue ở trên.
                # Nếu không rơi vào các if trên thì sleep và thử lại
                time.sleep(2)
                count += 1

            if count >= 40:
                bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="❌ Hết thời gian chờ (Timeout).")

        except Exception as e:
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"❌ Lỗi: {str(e)}")
