import requests
import time
import urllib.parse
import json
from telebot import types

def get_4mmo_code(web_url):
    """Hàm xử lý logic lấy mã từ 4mmo"""
    try:
        # Xử lý URL đầu vào
        web = web_url.strip()
        if not web.endswith("/"):
            web += "/"

        headers = {
            "accept": "*/*",
            "accept-language": "vi",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        # Bước 1: Request khởi tạo
        requests.get("https://4mmo.net/cd?&t=1", headers=headers, timeout=10)
        time.sleep(2) # Giảm thời gian chờ xuống chút cho bot nhanh hơn

        # Bước 2: Tạo URL load traffic
        encoded_web = urllib.parse.quote(web, safe='')
        url2 = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={encoded_web}&t=1"

        # Bước 3: Vòng lặp lấy mã (Giới hạn 20 lần thử ~ 40 giây để tránh treo bot)
        max_retries = 20
        for _ in range(max_retries):
            try:
                res2 = requests.get(url2, headers=headers, timeout=10)
                text2 = res2.text
                
                # Parse JSON
                try:
                    j = json.loads(text2)
                except json.JSONDecodeError:
                    time.sleep(2)
                    continue

                # Trường hợp 1: Lấy thành công
                if j.get("status") == 1 and j.get("data", {}).get("html"):
                    return True, j["data"]["html"]

                # Trường hợp 2: Đang chờ (#5)
                if j.get("status") == 0 and "#5" in j.get("message", ""):
                    time.sleep(2)
                    continue
                
                # Trường hợp 3: Sai Web (#1)
                if j.get("status") == 0 and "#1" in j.get("message", ""):
                    return False, "❌ Sai web lấy mã, vui lòng kiểm tra lại link!"

            except Exception as e:
                time.sleep(2)
                continue
        
        return False, "⏳ Hết thời gian chờ, vui lòng thử lại sau."

    except Exception as e:
        return False, f"Lỗi hệ thống: {str(e)}"

def register_mmo(bot):
    """Đăng ký lệnh /4mmo cho bot"""
    
    @bot.message_handler(commands=['4mmo'])
    def handle_4mmo(message):
        # Lấy tham số từ tin nhắn: /4mmo https://link...
        args = message.text.split()
        
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập link cần lấy mã.\nVí dụ: `/4mmo nhiệm vụ của link`", parse_mode="Markdown")
            return

        url = args[1]
        
        # Gửi tin nhắn đang xử lý
        msg = bot.reply_to(message, f"🔄 Đang lấy mã cho: {url}\nVui lòng đợi khoảng 10-30s...")

        # Gọi hàm xử lý
        ok, result = get_4mmo_code(url)

        if ok:
            # Nếu thành công
            bot.reply_to(message, f"✅ **Lấy mã thành công!**\n\nCode: `{result}`", parse_mode="Markdown")
            # Xóa tin nhắn "Đang lấy mã" cho gọn (tùy chọn)
            try:
                bot.delete_message(message.chat.id, msg.message_id)
            except:
                pass
        else:
            # Nếu thất bại
            bot.edit_message_text(f"⚠️ {result}", message.chat.id, msg.message_id)

