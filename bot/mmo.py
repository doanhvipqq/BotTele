import requests
import urllib.parse
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Config Headers
HEADERS = {
    "accept": "*/*",
    "accept-language": "vi",
    "user-agent": "Mozilla/5.0"
}

@Client.on_message(filters.command("4mmo", prefixes=[".", "/", "!"]))
async def get_4mmo_code(client: Client, message: Message):
    # Lấy tham số từ tin nhắn (URL)
    if len(message.command) < 2:
        return await message.reply("⚠️ Vui lòng nhập link cần lấy mã.\nVí dụ: `.4mmo https://google.com/`")
    
    web = message.command[1].strip()
    if not web.endswith("/"):
        web += "/"
    
    # Gửi tin nhắn thông báo đang xử lý
    msg = await message.reply("⏳ Đang kết nối tới 4mmo...")
    
    try:
        # Bước 1: Request khởi tạo
        requests.get("https://4mmo.net/cd?&t=1", headers=HEADERS)
        
        # Đợi 3 giây (Dùng asyncio để không chặn luồng của Bot)
        await msg.edit("⏳ Đang đợi server phản hồi (3s)...")
        await asyncio.sleep(3)
        
        # Bước 2: Tạo URL load traffic
        encoded_web = urllib.parse.quote(web, safe='')
        url2 = f"https://4mmo.net/load_traffic?&r=https%3A%2F%2Fwww.google.com%2F&w={encoded_web}&t=1"
        
        retry_count = 0
        max_retries = 30 # Giới hạn vòng lặp để tránh treo bot mãi mãi
        
        while retry_count < max_retries:
            res2 = requests.get(url2, headers=HEADERS)
            text2 = res2.text
            
            try:
                j = json.loads(text2)
            except json.JSONDecodeError:
                await asyncio.sleep(2)
                retry_count += 1
                continue

            # Trường hợp 1: Lấy được mã thành công
            if j.get("status") == 1 and j.get("data", {}).get("html"):
                code = j["data"]["html"]
                await msg.edit(f"✅ **Lấy mã thành công!**\n\n🌐 Web: `{web}`\n🔑 Code: `{code}`")
                return

            # Trường hợp 2: Đang chờ (#5)
            if j.get("status") == 0 and "#5" in j.get("message", ""):
                # Chỉ edit message mỗi 5 lần lặp để tránh spam API Telegram
                if retry_count % 3 == 0:
                    await msg.edit(f"⏳ Đang chờ mã... (Lần thử {retry_count})")
                
                await asyncio.sleep(2)
                retry_count += 1
                continue
            
            # Trường hợp 3: Sai web (#1)
            if j.get("status") == 0 and "#1" in j.get("message", ""):
                await msg.edit("❌ Sai web lấy mã, vui lòng kiểm tra lại link!")
                return

            # Các trường hợp lỗi khác
            retry_count += 1
            await asyncio.sleep(2)

        await msg.edit("❌ Quá thời gian chờ, không lấy được mã.")

    except Exception as e:
        await msg.edit(f"❌ Có lỗi xảy ra: {str(e)}")
