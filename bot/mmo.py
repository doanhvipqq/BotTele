import requests
import time
import urllib.parse
import json
from telebot import types

def get_4mmo_code(web_url):
    """Hàm xử lý logic lấy mã từ 4mmo (Đã fix lỗi timeout)"""
    try:
        web = web_url.strip()
        if not web.endswith("/"):
            web += "/"

        # Sử dụng Session để lưu cookie và kết nối ổn định như trình duyệt thật
        session = requests.Session()
        
        headers = {
            "accept": "*/*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "referer": "https://www.google.com/"
        }

        # Bước 1: Giả lập truy cập lần đầu
        session.get("https://4mmo.net/cd?&t=1", headers=headers, timeout=10)
        time.sleep(3) 

        # Bước 2: Tạo URL check mã
        encoded_web = urllib.parse.quote(web, safe='')
        url2 = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={encoded_web}&t=1"

        # Bước 3: Vòng lặp chờ mã
        # Tăng lên 60 lần thử x 2 giây = 120 giây (2 phút)
        max_retries = 60 
        
        for i in range(max_retries):
            try:
                res2 = session.get(url2, headers=headers, timeout=10)
                text2 = res2.text
                
                try:
                    j = json.loads(text2)
                except json.JSONDecodeError:
                    time.sleep(2)
                    continue

                # --- TRƯỜNG HỢP THÀNH CÔNG ---
                if j.get("status") == 1 and j.get("data", {}).get("html"):
                    return True, j["data"]["html"]

                # --- ĐANG ĐỢI (Web bắt chờ 60s) ---
                if j.get("status") == 0 and "#5" in j.get("message", ""):
                    # Vẫn đang đếm ngược, tiếp tục chờ
                    time.sleep(2)
                    continue
                
                # --- SAI WEB ---
                if j.get("status") == 0 and "#1" in j.get("message", ""):
                    return False, "❌ Sai link web lấy mã rồi, kiểm tra lại đi!"

            except Exception:
                time.sleep(2)
                continue
        
        return False, "⏳ Đã chờ quá 2 phút mà web chưa trả mã. Hãy thử lại thủ công."

    except Exception as e:
        return False, f"Lỗi Bot: {str(e)}"

def register_mmo(bot):
    
    @bot.message_handler(commands=['4mmo'])
    def handle_4mmo(message):
        args = message.text.split()
        
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Nhập thiếu link!\nCách dùng: `/4mmo link nhiệm vụ`", parse_mode="Markdown")
            return

        url = args[1]
        
        # Gửi tin nhắn xác nhận
        msg = bot.reply_to(message, f"🔄 Đang thực hiện nhiệm vụ cho: {url}\n\n⏳ **Vui lòng đợi khoảng 60 giây...**")

        # Gọi hàm xử lý
        ok, result = get_4mmo_code(url)

        if ok:
            # Gửi mã về
            bot.reply_to(message, f"✅ **LẤY MÃ THÀNH CÔNG!**\n\nCode: `{result}`", parse_mode="Markdown")
            # Xóa tin nhắn chờ
            try:
                bot.delete_message(message.chat.id, msg.message_id)
            except:
                pass
        else:
            # Gửi lỗi
            bot.edit_message_text(f"⚠️ {result}", message.chat.id, msg.message_id)
