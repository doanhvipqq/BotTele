import time
import requests
from bs4 import BeautifulSoup
from telebot.types import InputFile
from config import ADMIN_ID

def get_all_image_urls(bot, msg):
	headers = {"User-Agent": "Mozilla/5.0"}
	base_url = "https://cosplaytele.com/category/byoru/"

	all_images = []
	visited_albums = []

	try:
		response = requests.get(base_url, headers=headers, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		a_tags = soup.find_all("a", class_="page-number")
		if len(a_tags) >= 2:
			last_page = int(a_tags[-2].text)
			bot.edit_message_text(f"📄 Tổng số trang: {last_page}", msg.chat.id, msg.message_id)
		else:
			last_page = 1
			bot.edit_message_text("📄 Chỉ có 1 trang.", msg.chat.id, msg.message_id)

		for page in range(1, last_page + 1):
			bot.edit_message_text(f"➡️ Đang xử lý trang {page}/{last_page}...", msg.chat.id, msg.message_id)
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

			except Exception as e:
				bot.send_message(ADMIN_ID, f"⚠️ Lỗi tải trang {page}:\n{e}")
				continue

		# Lấy ảnh từ các album
		for index, album_url in enumerate(visited_albums, 1):
			bot.edit_message_text(
				f"🖼️ Đang lấy ảnh từ album {index}/{len(visited_albums)}...",
				msg.chat.id, msg.message_id
			)
			try:
				response = requests.get(album_url, headers=headers, timeout=10)
				soup = BeautifulSoup(response.text, "html.parser")

				for tag in soup.find_all(True):
					if tag.name == "strong" and "Recommend For You" in tag.text:
						break

					if tag.name == "img" and tag.has_attr("src") and \
						"attachment-full" in tag.get("class", []) and "size-full" in tag.get("class", []):
						
						src = tag['src']
						if src not in all_images:
							all_images.append(src)

			except Exception as err:
				bot.send_message(ADMIN_ID, f"⚠️ Lỗi album:\n{album_url}\n{err}")
				continue

			time.sleep(0.5)

	except Exception as e:
		bot.send_message(ADMIN_ID, f"❌ Lỗi tổng thể:\n{e}")
		return []

	bot.edit_message_text(f"✅ Đã thu thập xong {len(all_images)} ảnh.", msg.chat.id, msg.message_id)
	return all_images[::-1]  # đảo toàn bộ ảnh sau cùng


def register_img(bot):
	@bot.message_handler(commands=['img'])
	def handle_img(message):
		msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

		image_list = get_all_image_urls(bot, msg)

		try:
			if not image_list:
				bot.edit_message_text("❌ Không tìm thấy ảnh nào.", msg.chat.id, msg.message_id)
				return

			with open("cosplay_links.txt", "w", encoding="utf-8") as f:
				for url in image_list:
					f.write(url + "\n")

			bot.edit_message_text("📤 Đang gửi file...", msg.chat.id, msg.message_id)

			bot.send_document(
				message.chat.id,
				InputFile("cosplay_links.txt"),
				caption=f"📦 Tổng cộng: {len(image_list)} ảnh"
			)

		except Exception as e:
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi gửi file:\n{e}")
			bot.edit_message_text("❌ Gửi file thất bại.", msg.chat.id, msg.message_id)

		finally:
			bot.delete_message(msg.chat.id, msg.message_id)