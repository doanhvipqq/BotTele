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

def check_link(message, bot):
    url = message.text.strip()
    
    # Nếu người dùng chỉ gõ lệnh /bypass mà không kèm link
    if len(url.split()) < 2:
         bot.reply_to(message, "⚠️ Vui lòng nhập link sau lệnh. Ví dụ: `/bypass https://link...`")
         return

    # Lấy link từ tin nhắn (bỏ chữ /bypass ở đầu)
    user_link = url.split(" ", 1)[1]

    if not user_link.startswith("http"):
        bot.reply_to(message, "⚠️ Link không hợp lệ!")
        return

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
    except Exception as e:
        print(f"Lỗi Bypass: {e}")

    bot.edit_message_text("❌ Thất bại. API lỗi hoặc link không hỗ trợ.", 
                          chat_id=message.chat.id, 
                          message_id=msg.message_id)
