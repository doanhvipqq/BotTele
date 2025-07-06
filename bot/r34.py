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

			img_tags = soup.find_all("img")

			# Danh sách ảnh rác cần loại bỏ
			exclude_keywords = [
				"/r34chibi.png",
				"/icame.png"
			]

			for img in img_tags:
				src = img.get("src", "")
				if any(key in src for key in exclude_keywords):
					continue

				# Chuẩn hóa src thành URL đầy đủ
				if src.startswith("//"):
					src = "https:" + src
				elif src.startswith("/"):
					src = "https://rule34.xxx" + src

				# Gửi ảnh cho người dùng
				bot.send_photo(message.chat.id, src, reply_to_message_id=message.message_id)

				# Gửi về cho admin (ảnh + link gốc)
				bot.send_message(ADMIN_ID, f"🖼 Link ảnh: {src}\n🔗 Post: {response.url}")
				return

			bot.reply_to(message, "❌ Không tìm thấy ảnh nào hợp lệ.")

		except Exception as e:
			bot.reply_to(message, "❌ Đã xảy ra lỗi nội bộ. Admin đang xử lý.")
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý /r34:\n{e}")
