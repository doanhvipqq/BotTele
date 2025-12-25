import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

# --- CẤU HÌNH ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- HÀM XỬ LÝ LOGIC (CORE) ---
async def bypass_link4m_logic(url: str):
    async with aiohttp.ClientSession() as session:
        # === BƯỚC 1: LẤY TASK ID ===
        api_step1 = "https://api-v1-amber.vercel.app/api/v2/link4m"
        try:
            async with session.get(api_step1, params={"link": url}, headers=HEADERS) as resp1:
                data1 = await resp1.json()
                
                # Logic tìm task_id kỹ càng như code gốc
                task_id = data1.get("task_id")
                if not task_id and "data" in data1 and isinstance(data1["data"], dict):
                    task_id = data1["data"].get("task_id")

                if not task_id:
                    return {"status": False, "msg": f"❌ Lỗi Bước 1: Không lấy được Task ID.\nAPI trả về: {data1}"}
        except Exception as e:
            return {"status": False, "msg": f"❌ Lỗi kết nối Bước 1: {e}"}

        # === BƯỚC 2: CHỜ KẾT QUẢ (POLLING) ===
        api_step2 = "https://api-v1-amber.vercel.app/api/v2/getresult"
        
        # Thử 60 lần x 2 giây = 120 giây (2 phút)
        for i in range(60):
            try:
                async with session.get(api_step2, params={"task_id": task_id}, headers=HEADERS) as resp2:
                    data2 = await resp2.json()

                    # Kiểm tra URL kết quả
                    final_url = data2.get("url")
                    if not final_url and "data" in data2 and isinstance(data2["data"], dict):
                        final_url = data2["data"].get("url")

                    # Nếu có link -> Thành công
                    if final_url:
                        return {"status": True, "url": final_url}

                    # Nếu server báo success=False -> Vẫn đang xử lý -> Đợi tiếp
                    if data2.get("success") is False:
                        await asyncio.sleep(2) # Đợi 2s (không chặn bot)
                        continue
                    
                    # Lỗi lạ khác
                    return {"status": False, "msg": f"❌ Lỗi lạ từ API: {data2}"}

            except Exception as e:
                # Lỗi mạng khi đang chờ -> Thử lại chứ không hủy
                await asyncio.sleep(2)
        
        return {"status": False, "msg": "❌ Hết thời gian chờ (2 phút) mà server chưa trả Link."}

# --- HANDLER CỦA BOT ---
# Lệnh kích hoạt: /l4m [link]
@Client.on_message(filters.command("l4m"))
async def link4m_handler(client: Client, message: Message):
    # 1. Kiểm tra cú pháp
    if len(message.command) < 2:
        await message.reply_text("⚠️ **Sử dụng:** `/l4m <link>`", quote=True)
        return

    url = message.command[1]
    
    # 2. Gửi tin nhắn chờ
    status_msg = await message.reply_text(
        f"⏳ **Đang xử lý Link4M...**\n🔗 `{url}`\n\n_Bot đang chờ server trả kết quả (Max 2 phút)..._",
        quote=True,
        disable_web_page_preview=True
    )

    # 3. Gọi hàm xử lý
    result = await bypass_link4m_logic(url)

    # 4. Trả kết quả
    if result["status"]:
        await status_msg.edit_text(
            f"✅ **Bypass thành công!**\n\n🔗 Link gốc: {result['url']}",
            disable_web_page_preview=True
        )
    else:
        await status_msg.edit_text(result["msg"])
