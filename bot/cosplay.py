import random
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_cosplay(bot):
	@bot.message_handler(commands=['cosplay'])
	def handle_cosplay(message):
		headers = {"User-Agent": "Mozilla/5.0"}
		url = "https://cosplaytele.com/"

		try:
			# B1: Lấy số trang
			response = requests.get(url, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			a_tags = soup.find_all("a", class_="page-number")
			if len(a_tags) >= 2:
				last_page_number = int(a_tags[-2].text)
			else:
				last_page_number = 1

			# B2: Lấy danh sách album
			page = random.randint(1, last_page_number)
			url_page = f"https://cosplaytele.com/page/{page}/"
			response = requests.get(url_page, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			albums = []
			album_url = soup.select("div.box h5 a")[:24]
			for a in album_url:
				href = a.get("href", "")
				if href.startswith("https://"):
					albums.append(href)

			unique_albums = list(dict.fromkeys(albums))[:24]
			if not unique_albums:
				raise Exception("Không tìm thấy album nào.")

			# B3: Lấy ảnh từ 1 album ngẫu nhiên
			random_album = random.choice(unique_albums)
			response = requests.get(random_album, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			imgs = []

			img_tags = soup.select(".gallery-item img")
			for img in img_tags:
				src = img.get("src", "")
				if src and src.startswith("http") and src not in imgs:
					imgs.append(src)
			
			if not imgs:
				raise Exception("Không tìm thấy ảnh trong album.")
			
			random_img = random.choice(imgs)

			bot.send_photo(message.chat.id, random_img, reply_to_message_id=message.message_id)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /cosplay:\n{e}")
