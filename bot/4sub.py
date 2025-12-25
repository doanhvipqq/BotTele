import requests
import urllib.parse
# Đảm bảo bạn đã import bot instance, ví dụ: from main import bot

# --- PHẦN 1: HÀM XỬ LÝ (LOGIC) ---
def api_link4sub(target_url):
    """
    Hàm gọi API để bypass/xử lý link4sub
    """
    api = "https://api-v1-amber.vercel.app/api/v1/link4sub"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Mobile) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Referer": "https://api-v1-amber.vercel.app/",
        "Origin": "https://api-v1-amber.vercel.app"
    }
    
    params = {
        "url": target_url
    }
    
    try:
        # Giảm timeout xuống 10s để bot đỡ bị treo lâu nếu API chết
        r = requests.get(api, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "message": "API phản hồi quá lâu."}
    except Exception as e:
        return {"error": str(e), "status_code": getattr(r, "status_code", None) if 'r' in locals() else None}

# --- PHẦN 2: HANDLER CHO TELEGRAM BOT ---
# Lệnh sử dụng: /link4sub https://link-can-xu-ly
@bot.message_handler(commands=['link4sub', 'l4s'])
def handle_link4sub(message):
    try:
        # Lấy tham số sau lệnh (URL)
        parts = message.text.split()
        
        # Kiểm tra xem người dùng có nhập link không
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ <b>Cách dùng:</b> /link4sub <link_cần_xử_lý>", parse_mode="HTML")
            return

        url_to_process = parts[1].strip()
        
        # Gửi tin nhắn chờ
        msg_wait = bot.reply_to(message, "⏳ <i>Đang kết nối API...</i>", parse_mode="HTML")
        
        # Gọi hàm xử lý
        data = api_link4sub(url_to_process)
        
        # Xử lý kết quả trả về để hiển thị đẹp hơn
        if "data" in data and data["data"]:
            # Trường hợp thành công (dựa trên cấu trúc thường thấy của API này)
            result_link = data["data"]
            response_text = (
                f"✅ <b>Thành công!</b>\n"
                f"🔗 Link gốc: <code>{result_link}</code>"
            )
        elif "error" in data:
            # Trường hợp lỗi từ hàm gọi
            response_text = f"❌ <b>Lỗi:</b> {data.get('message', data['error'])}"
        else:
            # Trường hợp API trả về JSON lạ, in toàn bộ để debug
            response_text = f"ℹ️ <b>Kết quả API:</b>\n<code>{str(data)}</code>"

        # Edit lại tin nhắn chờ thành kết quả
        bot.edit_message_text(response_text, chat_id=message.chat.id, message_id=msg_wait.message_id, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"❌ Có lỗi xảy ra trong quá trình xử lý: {str(e)}")
      
