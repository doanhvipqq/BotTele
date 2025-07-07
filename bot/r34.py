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
			
			a_tags = soup.find_all("a", href=True)
			for a in a_tags:
				img = a.get("href", "")
				if img.startswith("https://wimg.rule34.xxx"):
					bot.send_photo(message.chat.id, img, reply_to_message_id=message.message_id)
					return  # Dừng ngay khi gửi được ảnh đầu tiên

			# Nếu không tìm thấy ảnh hợp lệ
			bot.reply_to(message, ERROR_MSG)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý /r34:\n{e}")
