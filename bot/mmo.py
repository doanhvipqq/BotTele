import requests
import asyncio
import urllib.parse
import json
from pyrogram import Client, filters
from pyrogram.types import Message

# --- CẤU HÌNH MODULE (Cho menu Help của Bot) ---
__MODULE__ = "MMO Tools"
__HELP__ = """
**Công cụ lấy mã 4MMO:**

• Cú pháp: `.j [link]`
• Ví dụ: `.j https://trumtruyen.vn/`
"""

# --- CODE CHÍNH ---
@Client.on_message(filters.command("j", prefixes=[".", "/", "!", "?"]) & filters.me)
async def get_code_mmo(client: Client, message: Message):
    """
    Hàm xử lý lấy mã 4mmo chạy trên Userbot
    """
    # 1. Lấy link từ tin nhắn người dùng nhập
    try:
        if len(message.command) < 2:
            await message.edit("⚠️ **Vui lòng nhập link!**\nVí dụ: `.j https://google.com`")
            return
        
        web = message.command[1].strip()
    except Exception:
        await message.edit("⚠️ **Lỗi cú pháp.**")
        return

    # Xử lý URL: thêm dấu / vào cuối nếu thiếu
    if not web.endswith("/"):
        web += "/"

    # 2. Thông báo trạng thái ban đầu
    status_msg = await message.edit(f"🔄 **Đang kết nối 4MMO...**\n🌐 Target: `{web}`")

    # Headers giả lập trình duyệt
    headers = {
        "accept": "*/*",
        "accept-language": "vi",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        # BƯỚC 1: Kích hoạt traffic (Request mở đầu)
        # Timeout 10s để tránh treo nếu mạng lag
        requests.get("https://4mmo.net/cd?&t=1", headers=headers, timeout=10)
        
        # Đợi 3s (dùng asyncio để không chặn luồng của bot)
        await asyncio.sleep(3)

        # Tạo URL kiểm tra mã
        encoded_web = urllib.parse.quote(web, safe='')
        url_check = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={encoded_web}&t=1"
        
        retry_count = 0
        max_retries = 40  # Giới hạn khoảng 80s (40 lần * 2s)

        # BƯỚC 2: Vòng lặp kiểm tra mã (Polling)
        while retry_count < max_retries:
            try:
                res = requests.get(url_check, headers=headers, timeout=10)
                j = res.json() # Tự động parse JSON
            except Exception:
                # Nếu lỗi mạng hoặc lỗi JSON, đợi 2s rồi thử lại
                await asyncio.sleep(2)
                retry_count += 1
                continue

            # --- TRƯỜNG HỢP 1: LẤY MÃ THÀNH CÔNG ---
            if j.get("status") == 1 and j.get("data", {}).get("html"):
                code = j["data"]["html"]
                await status_msg.edit(
                    f"✅ **LẤY MÃ THÀNH CÔNG**\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"🌐 Web: `{web}`\n"
                    f"🔑 Code: `{code}`"
                )
                return

            # --- TRƯỜNG HỢP 2: ĐANG CHỜ CLICK (Mã lỗi #5) ---
            if j.get("status") == 0 and "#5" in j.get("message", ""):
                # Cập nhật thông báo mỗi 5 lần thử (10s) để tránh spam edit limit
                if retry_count % 5 == 0:
                    await status_msg.edit(
                        f"⏳ **Đang đợi click...**\n"
                        f"🔗 Link: `{web}`\n"
                        f"⏱ Thời gian chờ: {retry_count * 2}s"
                    )
                
                await asyncio.sleep(2)
                retry_count += 1
                continue
            
            # --- TRƯỜNG HỢP 3: SAI WEB (Mã lỗi #1) ---
            if j.get("status") == 0 and "#1" in j.get("message", ""):
                await status_msg.edit(f"❌ **Sai Web!**\nLink `{web}` không đúng yêu cầu.")
                return

            # Các trường hợp khác: Đợi và thử lại
            retry_count += 1
            await asyncio.sleep(2)

        # BƯỚC 3: Xử lý khi hết thời gian chờ (Timeout)
        await status_msg.edit(f"❌ **Hết thời gian!**\nKhông tìm thấy mã sau {max_retries * 2} giây.")

    except Exception as e:
        # Bắt lỗi hệ thống (ví dụ: mất mạng, lỗi code)
        await status_msg.edit(f"❌ **Lỗi System:** `{str(e)}`")
