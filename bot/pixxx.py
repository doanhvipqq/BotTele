import re
import random
import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

def register_pixxx(bot):
	@bot.message_handler(commands=['pixxx'])
	def handle_pixxx(message):
		# Lấy số trang
		url_page = f"https://rule34.us/index.php?r=posts/index&q=rex_%28naruto_pixxx%29&page=0"
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

		response = requests.get(url_page, headers=headers, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		for a in soup.find_all("a"):
			if a.has_attr("alt") and a["alt"].lower() == "last page":
				href = a["href"]
				# Tách số trang từ chuỗi ?r=posts/index&q=...&page=40
				match = re.search(r"page=(\d+)", href)
				if match:
					last_page = int(match.group(1))
					page = random.randint(0, last_page)

					url = f"https://rule34.us/index.php?r=posts/index&q=rex_%28naruto_pixxx%29&page={page}"

					try:
						response = requests.get(url, headers=headers, timeout=10)
						soup = BeautifulSoup(response.text, "html.parser")

						a_tags = soup.find_all("a", id=True, href=True)
						post_urls = [tag.get("href", "") for tag in a_tags]
						if not post_urls:
							bot.reply_to(message, ERROR_MSG)
							return

						post_url = random.choice(post_urls)
							
						response = requests.get(post_url, headers=headers, timeout=15)
						soup = BeautifulSoup(response.text, "html.parser")

						img_tag = soup.find("img", src=True, alt=True)
						if not img_tag:
							bot.reply_to(message, ERROR_MSG)
							return

						img_url = img_tag.get("src", "")
						bot.send_photo(message.chat.id, img_url, reply_to_message_id=message.message_id)

					except Exception as e:
						bot.reply_to(message, ERROR_MSG)
						bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /pixxx:\n{e}")
