import re
import requests
from bs4 import BeautifulSoup
from telebot.types import InputFile
import os

from config import ADMIN_ID, ERROR_MSG  # Bạn có thể tự tạo file config.py

def get_all_pixxx_image_urls():
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
	}
	base_query = "naruto_pixxx"
	base_url = f"https://rule34.us/index.php?r=posts/index&q={base_query}&page="

	all_img_urls = []

	try:
		response = requests.get(base_url + "0", headers=headers, timeout=30)
		soup = BeautifulSoup(response.text, "html.parser")
		last_page = 0

		for a in soup.find_all("a"):
			if a.has_attr("alt") and a["alt"].lower() == "last page":
				match = re.search(r"page=(\d+)", a["href"])
				if match:
					last_page = int(match.group(1))
				break

		print(f"🔍 Tổng số trang: {last_page + 1}")

		for page in range(0, last_page + 1):
			print(f"📄 Đang xử lý trang {page}...")
			url = base_url + str(page)
			try:
				resp = requests.get(url, headers=headers, timeout=30)
				soup = BeautifulSoup(resp.text, "html.parser")

				post_links = [a['href'] for a in soup.find_all("a", id=True, href=True)]

				for post_url in post_links:
					try:
						post_resp = requests.get(post_url, headers=headers, timeout=30)
						post_soup = BeautifulSoup(post_resp.text, "html.parser")
						img_tag = post_soup.find("img", src=True, alt=True)
						if img_tag and img_tag['src'].startswith("http"):
							img_url = img_tag['src']
							all_img_urls.append(img_url)
							print(f"   → {img_url}")
					except Exception as err:
						print(f"⚠️ Lỗi tải post: {post_url} → {err}")
						continue

			except Exception as err:
				print(f"⚠️ Lỗi trang {page}: {err}")
				continue

	except Exception as e:
		print(f"❌ Lỗi tổng thể: {e}")
		return []

	return all_img_urls

def register_img1(bot):
	@bot.message_handler(commands=["img1"])
	def handle_img1(message):
		msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ...")

		try:
			img_urls = get_all_pixxx_image_urls()

			if not img_urls:
				bot.send_message(message.chat.id, "❌ Không tìm thấy ảnh nào.")
				return

			with open("pixxx_links.txt", "w", encoding="utf-8") as f:
				for url in img_urls:
					f.write(url + "\n")

			bot.send_document(
				message.chat.id,
				InputFile("pixxx_links.txt"),
				caption=f"📦 Đã thu thập: {len(img_urls)} ảnh"
			)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi xử lý /pixxx:\n{e}")

		finally:
			bot.delete_message(msg.chat.id, msg.message_id)
