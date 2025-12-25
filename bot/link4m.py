import asyncio
import aiohttp
from pyrogram import filters, Client
from pyrogram.types import Message

# --- CẤU HÌNH ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- HÀM XỬ LÝ LOGIC (CORE) ---
async def bypass_link4m_logic(url: str):
    async with aiohttp.ClientSession() as session:
        # BƯỚC 1: LẤY TASK ID
        try:
            async with session.get("https://api-v1-amber.vercel.app/api/v2/link4m", params={"link": url}, headers=HEADERS) as resp1:
                data1 = await resp1.json()
                task_id = data1.get("task_id")
                if not task_id and "data" in data1:
                    task_id = data1["data"].get("task_id")
                
                if not task_id:
                    return {"status": False, "msg": f"❌ Lỗi B1: Không lấy được Task ID.\nAPI: {data1}"}
        except Exception as e:
            return {"status": False, "msg": f"❌ Lỗi kết nối B1: {e}"}

        # BƯỚC 2: CHỜ KẾT QUẢ (Tối đa 2 phút)
        for i in range(60):
            try:
                async with session.get("https://api-v1-amber.vercel.app/api/v2/getresult", params={"task_id": task_id}, headers=HEADERS) as resp2:
                    data2 = await resp2.json()
                    
                    final_url = data2.get("url") or (data2.get("data") and data2["data"].get("url"))
                    
                    if final_url:
                        return {"status": True, "url": final_url}
                    
                    if data2.get("success") is False:
                        await asyncio.sleep(2)
                        continue
                    
                    return {"status": False, "msg": f"❌ Lỗi API: {data2}"}
            except:
                await asyncio.sleep(2)
        
        return {"status": False, "msg": "❌ Hết thời gian chờ (2 phút)."}

# --- HÀM ĐĂNG KÝ (QUAN TRỌNG: PHẢI CÓ HÀM NÀY ĐỂ KHỚP VỚI ẢNH CỦA BẠN) ---
def register_link4m(bot: Client):
    @bot.on_message(filters.command(["l4m", "bypass"]))
    async def link4m_handler(client: Client, message: Message):
        # 1. Kiểm tra input
        if len(message.command) < 2:
            await message.reply_text("⚠️ **Dùng lệnh:** `/l4m <link>`", quote=True)
            return

        url = message.command[1]
        
        # 2. Báo đang xử lý
        msg_wait = await message.reply_text(
            f"⏳ **Đang xử lý Link4M...**\n🔗 `{url}`\nBot sẽ chờ tối đa 2 phút...",
            quote=True,
            disable_web_page_preview=True
        )

        # 3. Gọi logic
        result = await bypass_link4m_logic(url)

        # 4. Trả kết quả
        if result["status"]:
            await msg_wait.edit_text(
                f"✅ **Bypass thành công!**\n\n🔗 Link gốc: {result['url']}",
                disable_web_page_preview=True
            )
        else:
            await msg_wait.edit_text(result["msg"])
                    
