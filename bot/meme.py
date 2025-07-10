import random
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_meme(bot):
	@bot.message_handler(commands=['meme'])
	def handle_meme(message):
		page = random.randint(1, 50)
		url = f"https://www.aigei.com/s?q=meme&dim=gif-picture_2&page={page}"
		headers = {
			"Referer": url,
			"User-Agent": "Mozilla/5.0",
		}

		try:
			response = requests.get(url, headers=headers, timeout=15)
			soup = BeautifulSoup(response.text, "html.parser")

			img_tags = soup.find_all("img", src=True)
			img_urls = []

			for tag in img_tags:
				img_url = tag.get("src", "")
				if img_url.startswith("//s1.aigei.com"):
					full_url = "https:" + img_url
					img_urls.append(full_url)

			if not img_urls:
				bot.reply_to(message, ERROR_MSG)
				return			

			random_url = random.choice(img_urls)
			bot.send_animation(message.chat.id, random_url, reply_to_message_id=message.message_id)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /meme:\n{e}")
