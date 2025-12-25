import time
import requests
import threading
from telebot import TeleBot

# --- CẤU HÌNH HEADERS ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- HÀM XỬ LÝ LOGIC (CHẠY NGẦM) ---
def bypass_process(bot, message, url, message_id_to_edit):
    """Hàm này sẽ chạy trong một luồng riêng để không làm đơ bot"""
    try:
        # === BƯỚC 1: LẤY TASK ID ===
        api_step1 = "https://api-v1-amber.vercel.app/api/v2/link4m"
        response1 = requests.get(api_step1, params={"link": url}, headers=HEADERS)
        data1 = response1.json()

        task_id = data1.get("task_id")
        if not task_id and "data" in data1 and isinstance(data1["data"], dict):
            task_id = data1["data"].get("task_id")

        if not task_id:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id_to_edit,
                text=f"❌ Lỗi Bước 1: Không lấy được Task ID.\nAPI: {data1}"
            )
            return

        # === BƯỚC 2: CHỜ KẾT QUẢ (Tối đa 2 phút) ===
        api_step2 = "https://api-v1-amber.vercel.app/api/v2/getresult"
        params_step2 = {"task_id": task_id}

        for i in range(60): # 60 lần x 2s = 120s
            try:
                response2 = requests.get(api_step2, params=params_step2, headers=HEADERS)
                data2 = response2.json()

                # Kiểm tra link kết quả
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

                # Nếu chưa xong thì đợi
                if data2.get("success") is False:
                    time.sleep(2)
                    continue
                
                # Lỗi lạ
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id_to_edit,
                    text=f"❌ Lỗi lạ từ API: {data2}"
                )
                return

            except Exception as e:
                time.sleep(2) # Lỗi mạng thì thử lại
        
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

# --- HÀM ĐĂNG KÝ VÀO BOT ---
def register_link4m(bot: TeleBot):
    @bot.message_handler(commands=['l4m', 'bypass'])
    def handle_link4m(message):
        # 1. Tách lấy link từ tin nhắn
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Sử dụng: `/l4m <link>`", parse_mode="Markdown")
            return
        
        url = parts[1]

        # 2. Gửi tin nhắn chờ
        msg_wait = bot.reply_to(message, f"⏳ Đang xử lý link: {url}\n\nVui lòng chờ khoảng 1-2 phút...")
        
        # 3. Tạo luồng (Thread) để xử lý riêng (Quan trọng: Giúp bot không bị lag)
        # Chúng ta truyền bot, message gốc, link, và ID tin nhắn chờ vào để xử lý
        t = threading.Thread(target=bypass_process, args=(bot, message, url, msg_wait.message_id))
        t.start()
        
