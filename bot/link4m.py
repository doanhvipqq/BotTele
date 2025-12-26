import time
import requests
import threading
import json
from telebot import TeleBot

# --- 1. CẤU HÌNH HEADERS ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://link4m.co/',
    'Accept': 'application/json, text/plain, */*',
}

# --- 2. HÀM XỬ LÝ LOGIC (CHẠY NGẦM) ---
def bypass_process(bot, message, url, message_id_to_edit):
    try:
        # === BƯỚC 1: LẤY TASK ID (API V3) ===
        api_step1 = "https://api-v1-amber.vercel.app/api/v3/link4m"
        
        try:
            req1 = requests.get(api_step1, params={"link": url}, headers=HEADERS, timeout=15)
        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi mạng B1: {e}", message.chat.id, message_id_to_edit)
            return

        # Kiểm tra JSON
        try:
            data1 = req1.json()
        except json.JSONDecodeError:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id_to_edit,
                text=f"❌ API v3 trả về lỗi HTML:\n`{req1.text[:200]}`",
                parse_mode="Markdown"
            )
            return

        # Tìm Task ID
        task_id = data1.get("task_id")
        if not task_id and "data" in data1 and isinstance(data1["data"], dict):
            task_id = data1["data"].get("task_id")

        if not task_id:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id_to_edit,
                text=f"❌ Không lấy được Task ID.\nResponse: `{str(data1)}`",
                parse_mode="Markdown"
            )
            return

        # === BƯỚC 2: LẤY KẾT QUẢ (API V2) ===
        api_step2 = "https://api-v1-amber.vercel.app/api/v2/getresult"
        params_step2 = {"task_id": task_id}

        # Vòng lặp 60 lần (2 phút)
        for i in range(60):
            try:
                req2 = requests.get(api_step2, params=params_step2, headers=HEADERS, timeout=10)
                
                try:
                    data2 = req2.json()
                except:
                    time.sleep(2)
                    continue

                # Kiểm tra kết quả
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

                # Nếu chưa xong -> Đợi
                if data2.get("success") is False:
                    time.sleep(2)
                    continue
                
                # Lỗi lạ
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message_id_to_edit,
                    text=f"❌ API v2 lỗi: `{str(data2)}`",
                    parse_mode="Markdown"
                )
                return

            except Exception:
                time.sleep(2)
        
        # Hết giờ
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id_to_edit,
            text="❌ Hết thời gian chờ (2 phút)."
        )

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id_to_edit,
            text=f"❌ Lỗi hệ thống: `{str(e)}`",
            parse_mode="Markdown"
        )

# --- 3. HÀM ĐĂNG KÝ ---
def register_link4m(bot: TeleBot):
    @bot.message_handler(commands=['l4m', 'bypass'])
    def handle_link4m(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Dùng: `/l4m <link>`")
            return
        
        url = parts[1]
        msg = bot.reply_to(message, f"⏳ Đang xử lý: {url}...")
        
        t = threading.Thread(target=bypass_process, args=(bot, message, url, msg.message_id))
        t.start()
            
        
