import requests
import asyncio
import urllib.parse
import json
from pyrogram import Client, filters
from pyrogram.types import Message

# Lệnh kích hoạt: .mmo [link]
# Ví dụ: .mmo https://trumtruyen.vn/
@Client.on_message(filters.command("mmo", prefixes=[".", "/", "!", "?"]) & filters.me)
async def get_code_mmo(client: Client, message: Message):
    # 1. Lấy link từ tin nhắn
    try:
        web = message.text.split(None, 1)[1].strip()
    except IndexError:
        await message.edit("⚠️ **Vui lòng nhập link cần lấy mã.**\nVí dụ: `.mmo https://google.com/`")
        return

    # Xử lý URL: thêm dấu / vào cuối nếu thiếu
    if not web.endswith("/"):
        web += "/"

    # 2. Thông báo đang xử lý
    await message.edit(f"🔄 **Đang kết nối 4mmo...**\nTarget: `{web}`")

    headers = {
        "accept": "*/*",
        "accept-language": "vi",
        "user-agent": "Mozilla/5.0"
    }

    try:
        # Bước 1: Gọi link kích hoạt (tương tự requests.get trong code gốc)
        requests.get("https://4mmo.net/cd?&t=1", headers=headers)
        
        # Đợi 3s như code gốc (dùng asyncio để không chặn luồng bot)
        await asyncio.sleep(3)

        # Tạo URL check traffic
        url_check = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={urllib.parse.quote(web, safe='')}&t=1"
        
        retry_count = 0
        max_retries = 40  # Giới hạn khoảng 80s (40 lần * 2s)

        # Bước 2: Vòng lặp kiểm tra mã
        while retry_count < max_retries:
            res = requests.get(url_check, headers=headers)
            try:
                # Parse JSON
                j = json.loads(res.text)
            except Exception:
                # Nếu lỗi json thì thử lại sau 2s
                await asyncio.sleep(2)
                retry_count += 1
                continue

            # --- TRƯỜNG HỢP 1: THÀNH CÔNG ---
            if j.get("status") == 1 and j.get("data", {}).get("html"):
                code = j["data"]["html"]
                await message.edit(
                    f"✅ **LẤY MÃ THÀNH CÔNG**\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"🌐 Web: `{web}`\n"
                    f"🔑 Code: `{code}`"
                )
                return

            # --- TRƯỜNG HỢP 2: ĐANG CHỜ TRAFFIC (#5) ---
            if j.get("status") == 0 and "#5" in j.get("message", ""):
                # Cứ mỗi 5 lần thử (10s) thì edit log 1 lần để tránh spam edit
                if retry_count % 5 == 0:
                    await message.edit(f"⏳ **Đang đợi click...**\nLink: `{web}`\nTime: {retry_count * 2}s")
                
                await asyncio.sleep(2)
                retry_count += 1
                continue
            
            # --- TRƯỜNG HỢP 3: SAI WEB (#1) ---
            if j.get("status") == 0 and "#1" in j.get("message", ""):
                await message.edit(f"❌ **Sai web lấy mã!**\nVui lòng kiểm tra lại link: `{web}`")
                return

            # Các lỗi khác
            retry_count += 1
            await asyncio.sleep(2)

        # Hết thời gian chờ
        await message.edit(f"❌ **Time out!**\nKhông tìm thấy mã sau {max_retries * 2} giây.")

    except Exception as e:
        await message.edit(f"❌ **Lỗi System:** `{str(e)}`")
