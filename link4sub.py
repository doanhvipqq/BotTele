# File: bot/link4sub.py
import requests

def register_link4sub(bot):
    # --- Hàm xử lý logic ---
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

    # --- Handler cho bot ---
    @bot.message_handler(commands=['link4sub', 'l4s'])
    def handle_link4sub(message):
        try:
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "⚠️ Cách dùng: /link4sub <link>")
                return
            
            msg_wait = bot.reply_to(message, "⏳ Đang xử lý...")
            data = api_link4sub(parts[1].strip())
            
            if "data" in data and data["data"]:
                bot.edit_message_text(f"✅ Link gốc: {data['data']}", message.chat.id, msg_wait.message_id)
            elif "error" in data:
                bot.edit_message_text(f"❌ Lỗi: {data['error']}", message.chat.id, msg_wait.message_id)
            else:
                bot.edit_message_text(f"❌ Lỗi không xác định: {data}", message.chat.id, msg_wait.message_id)
                
        except Exception as e:
            bot.reply_to(message, f"Lỗi hệ thống: {e}")
            
