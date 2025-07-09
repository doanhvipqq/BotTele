import random
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_pixxx(bot):
	@bot.message_handler(commands=['pixxx'])
	def handle_pixxx(message):
		page = random.randint(1, 4)
		url = f"https://narutopixxx.com/characters/all?page={page}"

		headers = {
			"Referer": url,
			"User-Agent": "Mozilla/5.0",
		}

		try:
			response = requests.get(url, headers=headers, timeout=15)
			soup = BeautifulSoup(response.text, "html.parser")

			img_tags = soup.find_all("img", class_="card-img-top")
			img_urls = []

			for tag in img_tags:
				img_url = tag.get("src", "")
				img_urls.append(img_url)

			if img_urls:
				random_url = random.choice(img_urls)
				bot.send_animation(message.chat.id, random_url, reply_to_message_id=message.message_id)
				return  # Dừng ngay khi gửi được ảnh đầu tiên

			# Nếu không tìm thấy ảnh hợp lệ
			bot.reply_to(message, ERROR_MSG)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /pixxx:\n{e}")
