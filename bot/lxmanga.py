import re
import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telebot.types import InputFile

def register_lxmanga(bot):
	@bot.message_handler(commands=['lxmanga'])
	def handle_lxmanga(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2 or not args[1].strip().startswith("https://lxmanga."):
			return bot.reply_to(message, "❗️Bạn cần nhập đúng định dạng: /lxmanga [url chương]", parse_mode="Markdown")
		chap_url = args[1].strip()

		sent_msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

		try:
			zip_data, total, story_name = get_zip_from_chapter(chap_url)

			if total == 0:
				return bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
											 text="❌ Không tìm thấy ảnh nào trong trang.")

			bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

			safe_file_name = clean_filename(story_name) + ".zip"

			bot.send_document(
				chat_id=message.chat.id,
				document=InputFile(zip_data, safe_file_name),
				caption=f"📦 {total} ảnh của truyện:\n*{story_name}*",
				reply_to_message_id=message.message_id,
				parse_mode="Markdown"
			)

		except Exception as e:
			bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
								  text=f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")

	def get_zip_from_chapter(chap_url):
		headers = {
			"Referer": chap_url,
			"User-Agent": "Mozilla/5.0",
		}

		response = requests.get(chap_url, headers=headers, timeout=10)
		response.raise_for_status()
		soup = BeautifulSoup(response.text, "html.parser")

		story_name = get_names_from_title(soup)

		img_divs = soup.select("div.text-center div.lazy")
		img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]

		zip_buffer = BytesIO()
		with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
			for idx, img_url in enumerate(img_urls):
				try:
					ext = urlparse(img_url).path.split(".")[-1].split("?")[0] or "jpg"
					filename = f"{idx+1:03d}.{ext}"
					zip_path = f"{clean_filename(story_name)}/{filename}"
					img_data = requests.get(img_url, headers=headers, timeout=10).content
					zipf.writestr(zip_path, img_data)
				except Exception:
					continue

		zip_buffer.seek(0)
		return zip_buffer, len(img_urls), story_name

	def get_names_from_title(soup):
		a_tag = soup.find("a", class_="text-ellipsis font-semibold hover:text-blue-500")
		if a_tag:
			story_name = a_tag.get_text(strip=True)
			return story_name

		return "Unknown"

	def clean_filename(name):
		return re.sub(r'[\\/*?:"<>|]', " ", name).strip()
