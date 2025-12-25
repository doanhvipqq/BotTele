import requests

def register_link4sub(bot):
    # --- Hàm gọi API ---
    def api_link4sub(target_url):
        api = "https://api-v1-amber.vercel.app/api/v1/link4sub"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; Mobile) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://api-v1-amber.vercel.app/"
        }
        try:
            r = requests.get(api, headers=headers, params={"url": target_url}, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    # --- Handler xử lý lệnh ---
    @bot.message_handler(commands=['link4sub', 'l4s'])
    def handle_link4sub(message):
        try:
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "Thiếu link!")
                return
            
            msg_wait = bot.reply_to(message, "...")
            
            url_can_xu_ly = parts[1].strip()
            data = api_link4sub(url_can_xu_ly)
            
            # --- PHẦN QUAN TRỌNG ĐÃ SỬA ---
            if "data" in data and data["data"]:
                # Lấy cụ thể trường 'destination_url' thay vì lấy cả cục
                # Dùng .get để tránh lỗi nếu API đổi cấu trúc
                result_link = data["data"].get("destination_url", "Không tìm thấy link đích")
                
                # Trả về kết quả chỉ có link (Gọn, đẹp)
                bot.edit_message_text(f"🔗 {result_link}", chat_id=message.chat.id, message_id=msg_wait.message_id)
            
            elif "error" in data:
                bot.edit_message_text(f"Lỗi: {data['error']}", chat_id=message.chat.id, message_id=msg_wait.message_id)
            else:
                bot.edit_message_text("Lỗi không xác định.", chat_id=message.chat.id, message_id=msg_wait.message_id)
                
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")
            
