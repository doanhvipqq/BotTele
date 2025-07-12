import random
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_cosplay(bot):
	@bot.message_handler(commands=['cosplay'])
	def handle_cosplay(message):
		headers = {"User-Agent": "Mozilla/5.0"}
		url = "https://cosplaytele.com/category/cosplay/"

		try:
			response = requests.get(url, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			a_tags = soup.find_all("a", class_="page-number")
			last_page_number = a_tags[-2]

			page = random.randint(1, int(last_page_number.text))
			url_page = f"https://cosplaytele.com/page/{page}/"


			response = requests.get(url_page, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			albums = []
			album_url = soup.find_all("a", href=True, class_="plain")[:24]


			for a in album_url:
				album = a.get("href", "")
				if album.startswith("https://"):
					albums.append(album)

			unique_albums = list(dict.fromkeys(albums))[:24]
			random_album = random.choice(unique_albums)

			response = requests.get(random_album, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			imgs = []
			img_url = soup.find_all("img", src=True, class_="attachment-full size-full", alt=True)

			for a in img_url:
				img = a.get("src", "")
				if img.startswith("https://"):
					imgs.append(img)

			random_img = random.choice(imgs)
			bot.send_photo(message.chat.id, random_img, reply_to_message_id=message.message_id)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /cosplay:\n{e}")
