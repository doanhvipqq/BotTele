import requests
import urllib.parse
import json
import time
from telebot import types

# Headers giả lập trình duyệt thật
HEADERS = {
    "Host": "4mmo.net",
    "Connection": "keep-alive",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://4mmo.net/",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
}

def register_mmo(bot):
    @bot.message_handler(commands=['4mmo'])
    def handle_4mmo_command(message):
        # 1. Xử lý đầu vào
        try:
            command_parts = message.text.split()
            if len(command_parts) < 2:
                bot.reply_to(message, "⚠️ Nhập link cần lấy mã.\nVD: /4mmo https://google.com/")
                return
            web = command_parts[1].strip()
            if not web.endswith("/"): 
                web += "/"
        except:
            bot.reply_to(message, "⚠️ Lỗi cú pháp.")
            return

        # 2. Gửi tin nhắn chờ
        msg = bot.reply_to(message, f"⏳ Đang kết nối lấy mã cho: {web}")
        chat_id = message.chat.id
        msg_id = msg.message_id

        # 3. Bắt đầu quy trình lấy mã
        try:
            # === QUAN TRỌNG: Dùng Session để lưu Cookies ===
            session = requests.Session()
            session.headers.update(HEADERS)

            # Bước 1: Request kích hoạt bộ đếm
            print(f"[4MMO] Bắt đầu request bước 1...")
            session.get("https://4mmo.net/cd?&t=1")
            
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="⏳ Đang đợi server đếm giây (3s)...")
            time.sleep(3) 

            # Bước 2: Chuẩn bị URL check
            encoded_web = urllib.parse.quote(web, safe='')
            # Lưu ý: 4mmo đôi khi check cả referrer ở url
            url_check = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={encoded_web}&t=1"

            retry = 0
            max_retries = 30 # Thử tối đa 30 lần (60 giây)

            while retry < max_retries:
                try:
                    res = session.get(url_check)
                    text_res = res.text
                    
                    # In ra console để debug nếu lỗi
                    # print(f"[4MMO Debug] {text_res}") 

                    # Cố gắng đọc JSON
                    try:
                        j = json.loads(text_res)
                    except json.JSONDecodeError:
                        # Nếu không phải JSON (có thể là HTML lỗi hoặc Cloudflare chặn)
                        print(f"[4MMO Lỗi] Server trả về không phải JSON: {text_res[:100]}...")
                        time.sleep(2)
                        retry += 1
                        continue

                    # --- PHÂN TÍCH KẾT QUẢ JSON ---
                    
                    # 1. Thành công
                    if j.get("status") == 1 and j.get("data", {}).get("html"):
                        code = j["data"]["html"]
                        bot.edit_message_text(
                            chat_id=chat_id, 
                            message_id=msg_id, 
                            text=f"✅ **THÀNH CÔNG**\n\n🔗 Web: `{web}`\n🔑 Code: `{code}`",
                            parse_mode="Markdown"
                        )
                        return

                    # 2. Đang đếm giây (Message chứa #5 hoặc status 0)
                    message_sv = j.get("message", "")
                    if j.get("status") == 0:
                        if "#5" in message_sv or "vui lòng đợi" in message_sv.lower():
                            if retry % 5 == 0:
                                bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"⏳ Vẫn đang chờ mã... ({retry})")
                        
                        elif "#1" in message_sv:
                            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="❌ Sai link web hoặc web không tồn tại trên hệ thống!")
                            return
                        else:
                            # Các lỗi khác
                            print(f"[4MMO Chờ] Status 0: {message_sv}")

                    time.sleep(2)
                    retry += 1

                except Exception as e_inner:
                    print(f"[4MMO Lỗi Loop] {e_inner}")
                    time.sleep(2)
                    retry += 1

            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="❌ Hết thời gian chờ (Timeout). Web traffic có thể đang bị lỗi.")

        except Exception as e:
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=f"❌ Lỗi bot: {str(e)}")
            print(f"[4MMO Crash] {e}")
