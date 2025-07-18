import time
import requests
from bs4 import BeautifulSoup
from telebot.types import InputFile
from config import ADMIN_ID

def get_all_image_urls(bot, msg):
	headers = {"User-Agent": "Mozilla/5.0"}
	base_url = "https://cosplaytele.com/category/byoru/"
	visited_albums = []
	all_images = []

	try:
		# Lấy số trang
		response = requests.get(base_url, headers=headers, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")
		a_tags = soup.find_all("a", class_="page-number")
		last_page = int(a_tags[-2].text) if len(a_tags) >= 2 else 1

		# Quét các album trên từng trang
		for page in range(1, last_page + 1):
			bot.edit_message_text(
				f"📄 Đang xử lý trang {page}/{last_page}...",
				msg.chat.id, msg.message_id
			)
			url_page = f"{base_url}page/{page}/"

			try:
				res = requests.get(url_page, headers=headers, timeout=10)
				soup = BeautifulSoup(res.text, "html.parser")

				for tag in soup.find_all("a", class_="plain"):
					href = tag.get("href")
					if href and href.startswith("http") and href not in visited_albums:
						visited_albums.append(href)

			except Exception as e:
				bot.send_message(ADMIN_ID, f"⚠️ Lỗi trang {page}:\n{e}")
				continue

		# Lấy ảnh từ từng album
		for index, album_url in enumerate(visited_albums, 1):
			bot.edit_message_text(
				f"🖼️ Lấy ảnh từ album {index}/{len(visited_albums)}...",
				msg.chat.id, msg.message_id
			)
			try:
				res = requests.get(album_url, headers=headers, timeout=10)
				soup = BeautifulSoup(res.text, "html.parser")

				for tag in soup.find_all("img", class_=["attachment-full", "size-full"]):
					if tag.has_attr("src"):
						all_images.append(tag["src"])

			except Exception as e:
				bot.send_message(ADMIN_ID, f"⚠️ Lỗi album:\n{album_url}\n{e}")
				continue

			time.sleep(0.5)

	except Exception as e:
		bot.send_message(ADMIN_ID, f"❌ Lỗi tổng thể:\n{e}")
		return []

	return all_images[::-1]  # đảo toàn bộ danh sách ảnh

def register_img(bot):
	@bot.message_handler(commands=['img'])
	def handle_img(message):
		msg = bot.reply_to(message, "⏳ Đang xử lý...")

		try:
			all_images = get_all_image_urls(bot, msg)

			if not all_images:
				bot.edit_message_text("❌ Không tìm thấy ảnh nào.", msg.chat.id, msg.message_id)
				return

			# Ghi ra file
			with open("cosplay_links.txt", "w", encoding="utf-8") as f:
				for url in all_images:
					f.write(url + "\n")

			bot.edit_message_text("📤 Đang gửi file...", msg.chat.id, msg.message_id)

			bot.send_document(
				message.chat.id,
				InputFile("cosplay_links.txt"),
				caption=f"📦 Tổng cộng: {len(all_images)} ảnh"
			)

		except Exception as e:
			bot.edit_message_text("❌ Đã xảy ra lỗi trong quá trình xử lý.", msg.chat.id, msg.message_id)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi xử lý /img:\n{e}")

		finally:
			bot.delete_message(msg.chat.id, msg.message_id)