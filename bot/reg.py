import requests
import time
from telebot import types

# Cấu hình API
API_URL = "https://keyherlyswar.x10.mx/Apidocs/reglq.php"
TIMEOUT = 10

def create_garena_account():
    """Gọi API để lấy thông tin tài khoản"""
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RegGarenaBot/1.0)"})
        res = session.get(API_URL, timeout=TIMEOUT)
        
        if res.status_code != 200:
            return False, f"Lỗi HTTP {res.status_code}"
            
        data = res.json()
        result = data.get("result")
        
        if not result or not isinstance(result, list):
            return False, "Dữ liệu API không hợp lệ"

        info = result[0]
        username = info.get("account") or info.get("username")
        password = info.get("password")
        
        if username and password:
            return True, (username, password)
        return False, "Không tìm thấy tài khoản"
    except Exception as e:
        return False, str(e)

def register_handlers(bot):
    """Đăng ký handler cho bot Telegram"""
    
    @bot.message_handler(commands=['reg'])
    def handle_reg(message):
        chat_id = message.chat.id
        args = message.text.split()
        qty = 1
        
        # Xử lý số lượng tài khoản
        if len(args) > 1:
            try:
                qty = int(args[1])
                if qty > 5:
                    return bot.reply_to(message, "⚠️ Giới hạn tối đa 5 tài khoản/lần.")
            except ValueError:
                return bot.reply_to(message, "❌ Vui lòng nhập số lượng hợp lệ (VD: /reg 3)")

        # Gửi thông báo đang xử lý
        status_msg = bot.reply_to(message, f"⏳ Đang thực hiện tạo {qty} tài khoản Garena...")
        
        results = []
        for i in range(qty):
            success, data = create_garena_account()
            if success:
                user, pwd = data
                # Sử dụng Markdown để người dùng chạm vào là copy được
                results.append(f"✅ **Acc {i+1}**:\n👤 User: `{user}`\n🔑 Pass: `{pwd}`")
            else:
                results.append(f"❌ **Acc {i+1}**: {data}")
            
            # Delay giữa các lần tạo tránh bị chặn
            if i < qty - 1:
                time.sleep(1)

        final_text = "🚀 **KẾT QUẢ REG GARENA** 🚀\n\n" + "\n\n".join(results)
        final_text += "\n\n⚠️ *Lưu ý: Không lưu trữ, hãy lưu lại thông tin ngay!*"
        
        bot.edit_message_text(final_text, chat_id, status_msg.message_id, parse_mode="Markdown")
