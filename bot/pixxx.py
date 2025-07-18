import re
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG
from telebot.types import InputFile

def register_pixxx(bot):
	@bot.message_handler(commands=['pixxx'])
	def handle_pixxx(message):
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
		}
		query = "rex_%28naruto_pixxx%29"
		base_url = f"https://rule34.us/index.php?r=posts/index&q={query}"

		try:
			# Lấy trang đầu để xác định tổng số trang
			response = requests.get(base_url + "&page=0", headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")

			last_page = 0
			for a in soup.find_all("a"):
				if a.has_attr("alt") and a["alt"].lower() == "last page":
					match = re.search(r"page=(\d+)", a["href"])
					if match:
						last_page = int(match.group(1))
					break

			image_urls = []

			for page in range(0, last_page + 1):
				url = f"{base_url}&page={page}"
				print(f"🔎 Đang xử lý trang {page}/{last_page}")
				try:
					resp = requests.get(url, headers=headers, timeout=10)
					soup = BeautifulSoup(resp.text, "html.parser")

					a_tags = soup.find_all("a", id=True, href=True)
					post_urls = [tag["href"] for tag in a_tags if tag["href"].startswith("/index.php?r=posts/view&id=")]

					for post_url in post_urls:
						full_post_url = "https://rule34.us" + post_url
						try:
							post_resp = requests.get(full_post_url, headers=headers, timeout=10)
							post_soup = BeautifulSoup(post_resp.text, "html.parser")

							img_tag = post_soup.find("img", src=True, alt=True)
							if img_tag:
								img_url = img_tag["src"]
								image_urls.append(img_url)

						except Exception as e:
							print(f"⚠️ Lỗi khi xử lý post: {post_url} – {e}")
							continue

				except Exception as e:
					print(f"⚠️ Lỗi khi tải trang {page}: {e}")
					continue

			if not image_urls:
				bot.reply_to(message, "❌ Không tìm thấy ảnh nào.")
				return

			# Ghi vào file txt
			with open("pixxx_links.txt", "w", encoding="utf-8") as f:
				for url in image_urls:
					f.write(url + "\n")

			bot.send_document(message.chat.id, InputFile("pixxx_links.txt"), caption=f"📦 Tổng cộng: {len(image_urls)} ảnh")

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /pixxx:\n{e}")