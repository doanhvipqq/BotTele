import requests
from config import ADMIN_ID
from bs4 import BeautifulSoup

def register_r34(bot):
	@bot.message_handler(commands=['r34'])
	def handle_r34(message):
		url = "https://rule34.xxx/index.php?page=post&s=random"
		headers = {
			"Referer": url,
			"User-Agent": "Mozilla/5.0",
		}

		try:
			response = requests.get(url, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")
	
			# Tìm tất cả thẻ <img>
			img_tags = soup.find_all("img")
	
			# Link ảnh bạn muốn loại trừ
			exclude_src = ["https://rule34.xxx/static/icame.png"]
	
			# In ra các src của ảnh
			for img in img_tags:
				src = img.get("src", "")
				if src in exclude_src:
					continue

				# Fix đường dẫn nếu bị thiếu scheme
				if src.startswith("//"):
					src = "https:" + src
				elif src.startswith("/"):
					src = "https://rule34.xxx" + src
	
				bot.send_photo(message.chat.id, src, reply_to_message_id=message.message_id)
				bot.send_message(ADMIN_ID, f"Link: {src}")
				return
	
			# Nếu không có ảnh phù hợp
			bot.reply_to(message, "❌ Không tìm thấy ảnh nào hợp lệ.")

		except Exception:
			bot.reply_to(message, "❌ Đã xảy ra lỗi nội bộ. Admin đang trong quá trình sửa chữa.")
