import requests
import time
from telebot import types

# Cấu hình từ file gốc của bạn
API_URL = "https://keyherlyswar.x10.mx/Apidocs/reglq.php"
TIMEOUT = 10

def create_garena_account():
    """Gọi API lấy tài khoản Garena"""
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RegGarenaBot/1.0)"})
        res = session.get(API_URL, timeout=TIMEOUT)
        
        if res.status_code != 200:
            return False, f"Lỗi HTTP {res.status_code}"
            
        data = res.json()
        result = data.get("result")
        
        if not result or not isinstance(result, list):
            return False, "API trả về dữ liệu trống"

        info = result[0]
        username = info.get("account") or info.get("username")
        password = info.get("password")
        
        if username and password:
            return True, (username, password)
        return False, "Không tìm thấy user/pass"
    except Exception as e:
        return False, str(e)

def register_handlers(bot):
    """Đăng ký handler cho bot theo cấu trúc BotTele"""
    
    @bot.message_handler(commands=['reg'])
    def handle_reg(message):
        chat_id = message.chat.id
        args = message.text.split()
        qty = 1
        
        # Xử lý số lượng tài khoản muốn tạo
        if len(args) > 1:
            try:
                qty = int(args[1])
                if qty > 5:
                    return bot.reply_to(message, "⚠️ Tối đa 5 acc/lần để tránh spam.")
            except ValueError:
                return bot.reply_to(message, "❌ Định dạng sai. Ví dụ: `/reg 3`")

        msg = bot.reply_to(message, f"⏳ Đang tạo {qty} tài khoản Garena...")
        
        results = []
        for i in range(qty):
            success, data = create_garena_account()
            if success:
                user, pwd = data
                # Định dạng để người dùng chạm vào là copy được ngay
                results.append(f"✅ **Acc {i+1}**:\n👤 User: `{user}`\n🔑 Pass: `{pwd}`")
            else:
                results.append(f"❌ **Acc {i+1}**: {data}")
            
            if i < qty - 1:
                time.sleep(1) # Delay tránh bị API block

        final_text = "🚀 **KẾT QUẢ REG GARENA** 🚀\n\n" + "\n\n".join(results)
        bot.edit_message_text(final_text, chat_id, msg.message_id, parse_mode="Markdown")
