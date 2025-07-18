import time
import requests
from bs4 import BeautifulSoup
from telebot.types import InputFile
from config import ADMIN_ID  # Thêm dòng này để lấy ID quản trị viên

def get_all_image_urls(bot):
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
			bot.send_message(ADMIN_ID, f"📄 Tổng số trang: {last_page}")
		else:
			last_page = 1
			bot.send_message(ADMIN_ID, "📄 Chỉ có 1 trang.")

		for page in range(1, last_page + 1):
			bot.send_message(ADMIN_ID, f"➡️ Đang xử lý trang {page}...")
			url_page = f"{base_url}page/{page}/"

			try:
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

				bot.send_message(ADMIN_ID, f"📸 Đã tìm thấy {len(visited_albums)} album.")

			except Exception as e:
				bot.send_message(ADMIN_ID, f"⚠️ Lỗi tải trang {page}:\n{e}")
				continue

		# Lấy ảnh từ các album
		for index, album_url in enumerate(visited_albums, 1):
			bot.send_message(ADMIN_ID, f"  → Đang lấy ảnh từ album {index}: {album_url}")
			try:
				response = requests.get(album_url, headers=headers, timeout=10)
				soup = BeautifulSoup(response.text, "html.parser")

				image_list = []
				for tag in soup.find_all(True):
					if tag.name == "strong" and "Recommend For You" in tag.text:
						break

					if tag.name == "img" and tag.has_attr("src") and \
						"attachment-full" in tag.get("class", []) and "size-full" in tag.get("class", []):
						
						src = tag['src']
						if src not in image_list:
							image_list.append(src)

				# ✅ Đảo ngược danh sách ảnh
				album_images[album_url] = image_list[::-1]

			except Exception as err:
				bot.send_message(ADMIN_ID, f"⚠️ Lỗi album:\n{album_url}\n{err}")
				continue

			time.sleep(0.5)

	except Exception as e:
		bot.send_message(ADMIN_ID, f"❌ Lỗi tổng thể:\n{e}")
		return {}

	total = sum(len(v) for v in album_images.values())
	bot.send_message(ADMIN_ID, f"✅ Tổng số ảnh thu được: {total}")
	return album_images


def register_img(bot):
	@bot.message_handler(commands=['img'])
	def handle_img(message):
		msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

		image_data = get_all_image_urls(bot)

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
