import requests
from bs4 import BeautifulSoup
from config import ADMIN_ID, ERROR_MSG

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
			
			img_tag = soup.find("img", id="image")
			if not img_tag:
				bot.reply_to(message, ERROR_MSG)
				return
				
			img_url = img_tag.get("src", "")
			bot.send_photo(message.chat.id, img_url, reply_to_message_id=message.message_id)

		except Exception as e:
			bot.reply_to(message, ERROR_MSG)
			bot.send_message(ADMIN_ID, f"⚠️ Lỗi khi xử lý lệnh /r34:\n{e}")
