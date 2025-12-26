import time
import requests
import threading
from telebot import TeleBot

# --- CẤU HÌNH HEADERS ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- HÀM XỬ LÝ LOGIC (CHẠY TRONG LUỒNG RIÊNG) ---
def bypass_process(bot, message, url, message_id_to_edit):
    """Hàm này chạy ẩn để không làm đơ bot khi chờ 2 phút"""
    try:
        # === BƯỚC 1: LẤY TASK ID (Dùng API v2 cho ổn định) ===
        api_step1 = "https://api-v1-amber.vercel.app/api/v3/link4m"
        response1 = requests.get(api_step1, params={"link": url}, headers=HEADERS)
        data1 = response1.json()

        task_id = data1.get("task_id")
        if not task_id and "data" in data1 and isinstance(data1["data"], dict):
            task_id = data1["data"].get("task_id")

        if not task_id:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id_to_edit,
                text=f"❌ Lỗi Bước 1: Không lấy được Task ID.\nAPI trả về: {data1}"
            )
            return

        # === BƯỚC 2: CHỜ KẾT QUẢ (Tối đa 2 phút) ===
        api_step2 = "https://api-v1-amber.vercel.app/api/v2/getresult"
        params_step2 = {"task_id": task_id}

        # Vòng lặp chờ (60 lần x 2 giây = 120 giây)
        for i in range(60):
            try:
                response2 = requests.get(api_step2, params=params_step2, headers=HEADERS)
                data2 = response2.json()

                # Kiểm tra xem có Link chưa
                final_url = data2.get("url")
                if not final_url and "data" in data2 and isinstance(data2["data"], dict):
                    final_url = data2["data"].get("url")

                if final_url:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message_id_to_edit,
                        text=f"✅ **Bypass thành công!**\n\n🔗 Link gốc: {final_url}",
                        parse_mode="Markdown"
                    )
                    return

                # Nếu server báo success=False nghĩa là đang giải -> Đợi tiếp
                if data2.get("success") is False:
                    time.sleep(2)
                    continue
                
                # Nếu server báo lỗi khác
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id_to_edit,
                    text=f"❌ Lỗi lạ từ API: {data2}"
                )
                return

            except Exception:
                time.sleep(2) # Lỗi mạng nhẹ thì thử lại, không báo lỗi ngay
        
        # Hết 60 vòng lặp (2 phút) mà chưa xong
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id_to_edit,
            text="❌ Hết thời gian chờ (2 phút) mà server chưa trả Link."
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id_to_edit,
            text=f"❌ Lỗi hệ thống: {str(e)}"
        )

# --- HÀM ĐĂNG KÝ VÀO BOT (BẮT BUỘC PHẢI CÓ) ---
def register_link4m(bot: TeleBot):
    @bot.message_handler(commands=['l4m', 'bypass'])
    def handle_link4m(message):
        # 1. Tách lấy link
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ **Cách dùng:** `/l4m <link>`", parse_mode="Markdown")
            return
        
        url = parts[1]

        # 2. Gửi tin nhắn chờ
        msg_wait = bot.reply_to(message, f"⏳ Đang xử lý: {url}\n\n_Vui lòng chờ 1-2 phút..._", parse_mode="Markdown")
        
        # 3. Tạo luồng (Thread) để xử lý riêng -> GIÚP BOT KHÔNG BỊ LAG
        t = threading.Thread(target=bypass_process, args=(bot, message, url, msg_wait.message_id))
        t.start()
        
