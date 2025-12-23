import requests
import time
from telebot import types

# Cấu hình từ file gốc của bạn
API_URL = "https://keyherlyswar.x10.mx/Apidocs/reglq.php"
TIMEOUT = 10

def get_garena_account():
    """Logic gọi API để lấy thông tin tài khoản"""
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; RegGarenaBot/1.0)"})
        res = session.get(API_URL, timeout=TIMEOUT)
        
        if res.status_code != 200:
            return None, f"Lỗi máy chủ (HTTP {res.status_code})"
            
        data = res.json()
        result = data.get("result")
        
        if not result or not isinstance(result, list):
            return None, "API không trả về dữ liệu"

        info = result[0]
        # Lấy thông tin account/password
        user = info.get("account") or info.get("username")
        pwd = info.get("password")
        
        if user and pwd:
            return (user, pwd), "Thành công"
        return None, "Dữ liệu tài khoản trống"
    except Exception as e:
        return None, f"Lỗi kết nối: {str(e)}"

def register_garena_handlers(bot):
    """Đăng ký các xử lý lệnh phù hợp với BotTele"""
    
    @bot.message_handler(commands=['garena'])
    def handle_garena_cmd(message):
        chat_id = message.chat.id
        args = message.text.split()
        quantity = 1
        
        # Kiểm tra tham số số lượng (VD: /garena 3)
        if len(args) > 1:
            try:
                quantity = int(args[1])
                if quantity > 5:
                    return bot.reply_to(message, "⚠️ Để tránh bị chặn, bạn chỉ có thể tạo tối đa 5 acc/lần.")
                if quantity <= 0:
                    return bot.reply_to(message, "❌ Số lượng không hợp lệ.")
            except ValueError:
                return bot.reply_to(message, "❌ Vui lòng nhập số. VD: `/garena 3`")

        # Thông báo trạng thái ban đầu
        status_msg = bot.reply_to(message, f"🔄 Đang khởi tạo {quantity} tài khoản...")
        
        final_output = []
        for i in range(quantity):
            acc_data, status_text = get_garena_account()
            
            if acc_data:
                user, pwd = acc_data
                # Định dạng Markdown: Chạm vào là copy
                final_output.append(f"🎁 **Acc {i+1}**:\n👤 User: `{user}`\n🔑 Pass: `{pwd}`")
            else:
                final_output.append(f"❌ **Acc {i+1}**: {status_text}")
            
            # Delay 1 giây giữa các lần tạo theo logic gốc
            if i < quantity - 1:
                time.sleep(1)

        # Cập nhật tin nhắn kết quả cuối cùng
        response_text = "🚀 **KẾT QUẢ TẠO ACC GARENA** 🚀\n\n" + "\n\n".join(final_output)
        response_text += "\n\n⚠️ *Hãy đổi mật khẩu ngay sau khi nhận!*"
        
        bot.edit_message_text(
            text=response_text,
            chat_id=chat_id,
            message_id=status_msg.message_id,
            parse_mode="Markdown"
        )
