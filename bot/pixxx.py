import random
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_pixxx(bot):
	@bot.message_handler(commands=['pixxx'])
	def handle_pixxx(message):
		page = random.randint(1, 41)
		url = f"https://rule34.us/index.php?r=posts/index&q=rex_%28naruto_pixxx%29&page={page}"

		headers = {
			"Referer": url,
			"User-Agent": "Mozilla/5.0",
		}

		try:
			response = requests.get(url, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			a_tags = soup.find_all("a", id=True, href=True)
			post_urls = [tag.get("href", "") for tag in a_tags]
			if post_urls:
				random_post = random.choice(post_urls)
				# bot.send_photo(message.chat.id, random_url, reply_to_message_id=message.message_id)
				try:
					response = requests.get(random_post, headers=headers, timeout=15)
					soup = BeautifulSoup(response.text, "html.parser")

					img_tags = soup.find_all("img", src=True, alt=True)
					for tag in img_tags:
						img_url = tag.get("src", "")
						bot.send_photo(message.chat.id, img_url, reply_to_message_id=message.message_id)
					

					# Nếu không tìm thấy ảnh hợp lệ
					# bot.reply_to(message, ERROR_MSG)
				except Exception as e:
					bot.reply_to(message, ERROR_MSG)
					bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /pixxx:\n{e}")

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /pixxx:\n{e}")
