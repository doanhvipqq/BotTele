import time
import requests
import threading
import json
from telebot import TeleBot

# --- 1. CẤU HÌNH HEADERS ---
# Giả lập trình duyệt (Chrome) để hạn chế bị chặn
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://link4m.co/',
    'Accept': 'application/json, text/plain, */*',
}

# --- 2. HÀM XỬ LÝ LOGIC (CHẠY NGẦM) ---
def bypass_process(bot, message, url, message_id_to_edit):
    """
    Hàm xử lý chạy trong luồng riêng.
    Quy trình: API v3 (Lấy Task) -> API v2 (Lấy Kết quả)
    """
    try:
        # === BƯỚC 1: GỬI LINK (DÙNG API V3) ===
        api_step1 = "https://api-v1-amber.vercel.app/api/v3/link4m"
        
        try:
            req1 = requests.get(api_step1, params={"link": url}, headers=HEADERS, timeout=15)
        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi mạng (Bước 1): {e}", message.chat.id, message_id_to_edit)
            return

        # [QUAN TRỌNG] Kiểm tra xem server trả về JSON hay HTML lỗi
        try:
            data1 = req1.json()
        except json.JSONDecodeError:
            # Nếu lỗi này xảy ra, nghĩa là API chết hoặc bị chặn
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id_to_edit,
                text=f"❌ **API v3 Lỗi!**\nServer trả về HTML thay vì JSON.\nNội dung: `{req1.text[:200]}`", # In ra lỗi thực sự
                parse_mode="Markdown"
            )
            return

        # Lấy Task ID
        task_id = data1.get("task_id")
        if not task_id and "data" in data1 and isinstance(data1["data"], dict):
            task_id = data1["data"].get("task_id")

        if not task_id:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id_to_edit,
                text=f"❌ Không lấy được Task ID.\nAPI v3 phản hồi: `{str(data1)}`",
                parse_mode="Markdown"
            )
            return

        # === BƯỚC 2: CHỜ KẾT QUẢ (DÙNG API V2) ===
        api_step2 = "https://api-v1-amber.vercel.app/api/v2/getresult"
        params_step2 = {"task_id": task_id}

        # Vòng lặp chờ (60 lần x 2 giây = 120 giây)
        for i in range(60): 
            try:
                req2 = requests.get(api_step2, params=params_step2, headers=HEADERS, timeout=10)
                
                try:
                    data2 = req2.json()
                except:
                    time.sleep(2)
                    continue

                # 1. Kiểm tra link kết quả
                final_url = data2.get("url")
                if not final_url and "data" in data2 and isinstance(data2["data"], dict):
                    final_url = data2["data"].get("url")

                if final_url:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message_id_to_edit,
                        text=f"✅ **Bypass thành công!**\n\n🔗 Link gốc: `{final_url}`",
                        parse_mode="Markdown"
                    )
                    return

                # 2. Nếu đang xử lý (success = False) -> Đợi
                if data2.get("success") is False:
                    time.sleep(2)
                    continue
                
                # 3. Lỗi lạ từ API
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id_to_edit,
                    text=f"❌ API v2 báo lỗi: `{str(data2)}`",
                    parse_mode="Markdown"
                )
                return

            except Exception:
                time.sleep(2) # Lỗi mạng nhẹ thì thử lại
        
        # Hết 2 phút
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id_to_edit,
            text="❌ Hết thời gian chờ (2 phút) mà server chưa trả Link."
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id_to_edit,
            text=f"❌ Lỗi hệ thống: `{str(e)}`",
            parse_mode="Markdown"
        )

# --- 3. HÀM ĐĂNG KÝ (ĐỂ MAIN.PY GỌI) ---
def register_link4m(bot: TeleBot):
    @bot.message_handler(commands=['l4m', 'bypass'])
    def handle_link4m(message):
        # 1. Kiểm tra cú pháp
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ **Cách dùng:** `/l4m <link>`", parse_mode="Markdown")
            return
        
        url = parts[1]

        # 2. Gửi tin nhắn chờ
        msg_wait = bot.reply_to(message, f"⏳ **Đang xử lý...**\n🔗 `{url}`\n_(API v3 -> v2)_", parse_mode="Markdown")
        
        # 3. Tạo luồng (Thread)
        t = threading.Thread(target=bypass_process, args=(bot, message, url, msg_wait.message_id))
        t.start()
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
        
