import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_r34(bot):
    @bot.message_handler(commands=['r34'])
    def handle_r34(message):
        url = "https://rule34.xxx/index.php?page=post&s=random"
        headers = {
            "Referer": url,
            "User-Agent": "Mozilla/5.0",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            img_tags = soup.find_all("img")

            exclude_src = [
                "/images/r34chibi.png",
                "https://rule34.xxx/static/icame.png"
            ]

            for img in img_tags:
                src = img.get("src", "")
                if not src or src in exclude_src:
                    continue

                # Gửi ảnh cho người dùng
                bot.send_photo(message.chat.id, src, reply_to_message_id=message.message_id)
                return

            # Nếu không tìm thấy ảnh hợp lệ
            bot.reply_to(message, ERROR_MSG)

        except Exception as e:
            bot.reply_to(message, ERROR_MSG)
            bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý /r34:\n{e}")