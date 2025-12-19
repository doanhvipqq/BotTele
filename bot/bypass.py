# File: bot/bypass.py
import requests

# Headers giả lập trình duyệt
HEADERS = {
    "Host": "bypass.bot.nu",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Referer": "https://bypass.bot.nu/"
}

# --- HÀM CHÍNH ĐƯỢC GỌI TỪ MAIN.PY ---
def register_bypass(bot):
    
    # Đăng ký lệnh /bypass để bot lắng nghe
    @bot.message_handler(commands=['bypass'])
    def handle_bypass_command(message):
        url_text = message.text.strip()
        
        # Kiểm tra xem người dùng có nhập link không
        # Split ra thành ['/bypass', 'link...']
        if len(url_text.split()) < 2:
             bot.reply_to(message, "⚠️ Vui lòng nhập link sau lệnh.\nVí dụ: `/bypass https://link...`", parse_mode="Markdown")
             return

        # Lấy link từ tin nhắn (bỏ chữ /bypass ở đầu)
        user_link = url_text.split(" ", 1)[1].strip()

        if not user_link.startswith("http"):
            bot.reply_to(message, "⚠️ Link không hợp lệ! Phải bắt đầu bằng http hoặc https.")
            return

        # Gửi tin nhắn chờ
        msg = bot.reply_to(message, "⏳ **Đang bypass Linkvertise...**", parse_mode="Markdown")

        try:
            api_url = f"https://bypass.bot.nu/bypass2?url={user_link}"
            response = requests.get(api_url, headers=HEADERS, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "destination" in data and data["destination"]:
                    final_link = data["destination"]
                    bot.edit_message_text(f"✅ **Bypass thành công!**\n\n🔗 Link gốc: `{final_link}`", 
                                          chat_id=message.chat.id, 
                                          message_id=msg.message_id, 
                                          parse_mode="Markdown")
                    return
            
            # Nếu API trả về 200 nhưng không có destination hoặc lỗi khác
            bot.edit_message_text("❌ Không tìm thấy link đích. API trả về dữ liệu rỗng.", 
                                  chat_id=message.chat.id, 
                                  message_id=msg.message_id)

        except Exception as e:
            print(f"Lỗi Bypass: {e}")
            bot.edit_message_text(f"❌ Thất bại. Lỗi kết nối hoặc API hỏng.\nChi tiết: {e}", 
                                  chat_id=message.chat.id, 
                                  message_id=msg.message_id)
