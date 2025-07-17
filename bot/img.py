import time
import requests
from bs4 import BeautifulSoup
from telebot.types import InputFile

def get_all_image_urls():
	headers = {"User-Agent": "Mozilla/5.0"}
	base_url = "https://cosplaytele.com/category/byoru/"

	album_images = {}
	visited_albums = []

	try:
		response = requests.get(base_url, headers=headers, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		a_tags = soup.find_all("a", class_="page-number")
		if len(a_tags) >= 2:
			last_page = int(a_tags[-2].text)
			print(f"Tổng số trang: {last_page}")
		else:
			last_page = 1
			print("Chỉ có 1 trang.")

		for page in range(1, last_page + 1):
			print(f"Đang xử lý trang {page}...")
			url_page = f"{base_url}page/{page}/"

			response = requests.get(url_page, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			for tag in soup.find_all(True):
				if tag.name == "span" and tag.get("class") == ["section-title-main"]:
					if "Popular Cosplay" in tag.text:
						break

				if tag.name == "a" and tag.has_attr("href") and "plain" in tag.get("class", []):
					album_url = tag['href']
					if album_url not in visited_albums:
						visited_albums.append(album_url)

			print(f"Đã tìm thấy {len(visited_albums)} album.")

		# Lấy ảnh từ các album
		for index, album_url in enumerate(visited_albums, 1):
			print(f"  → Lấy ảnh từ album {index}: {album_url}")
			try:
				response = requests.get(album_url, headers=headers, timeout=10)
				soup = BeautifulSoup(response.text, "html.parser")

				for tag in soup.find_all(True):
					if tag.name == "strong" and "Recommend For You" in tag.text:
						break

					if tag.name == "img" and tag.has_attr("src") and \
						"attachment-full" in tag.get("class", []) and "size-full" in tag.get("class", []):
						
						src = tag['src']
						album_images.setdefault(album_url, [])
						if src not in album_images[album_url]:
							album_images[album_url].append(src)

			except Exception as err:
				print(f"    ⚠️ Lỗi album: {err}")

			time.sleep(0.5)

	except Exception as e:
		print(f"Lỗi tổng thể: {e}")

	total = sum(len(v) for v in album_images.values())
	print(f"\nTổng số ảnh thu được: {total}")
	return album_images


def register_img(bot):
	@bot.message_handler(commands=['img'])
	def handle_img(message):
		msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

		image_data = get_all_image_urls()

		try:
			if not image_data:
				bot.send_message(message.chat.id, "❌ Không tìm thấy ảnh nào.")
				return

			total = sum(len(v) for v in image_data.values())

			with open("cosplay_links.txt", "w", encoding="utf-8") as f:
				for urls in image_data.values():
					for url in urls:
						f.write(url + "\n")

			bot.send_document(
				message.chat.id,
				InputFile("cosplay_links.txt"),
				caption=f"📦 Tổng cộng: {total} ảnh"
			)
		finally:
			bot.delete_message(msg.chat.id, msg.message_id)
