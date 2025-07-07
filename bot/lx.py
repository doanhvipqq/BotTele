import re
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from telebot.types import InputFile

def register_lx(bot):
	@bot.message_handler(commands=['lx'])
	def handle_lx(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2 or not args[1].strip().startswith("https://lx."):
			return bot.reply_to(message, "❗️Bạn cần nhập đúng định dạng: /lx [url chương]", parse_mode="Markdown")
		chap_url = args[1].strip()

		sent_msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

		try:
			pdf_data, total, story_name = create_pdf_file(chap_url)

			if total == 0:
				return bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
											 text="❌ Không tìm thấy ảnh nào trong trang.")

			bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

			safe_file_name = clean_filename(story_name) + ".pdf"

			bot.send_document(
				chat_id=message.chat.id,
				document=InputFile(pdf_data, clean_filename(story_name) + ".pdf"),
				caption=f"📄 {total} trang PDF của truyện:\n<b>{story_name}</b>",
				reply_to_message_id=message.message_id,
			)


		except Exception as e:
			bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
								  text=f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")

	def clean_filename(name):
		return re.sub(r'[\\/*?:"<>|]', " ", name).strip()

	def get_name_manga(soup):
		a_tag = soup.find("a", class_="text-ellipsis font-semibold hover:text-blue-500")
		if a_tag:
			story_name = a_tag.get_text(strip=True)
			return story_name

		return "Unknown"

	def get_img_urls(soup):	
		img_urls = []	
		div_tags = soup.find_all("div", attrs={"data-src": True})
		for div in div_tags:
			img = div.get("data-src", "")
			# if img.startswith("https://s3.lxmanga.xyz/"):
			img_urls.append(img)
		return img_urls


	def create_pdf_file(chap_url):
		headers = {
			"Referer": chap_url,
			"User-Agent": "Mozilla/5.0",
		}

		response = requests.get(chap_url, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		story_name = get_name_manga(soup)
		img_urls = get_img_urls(soup)

		images = []
		for img_url in img_urls:
			try:
				img_data = requests.get(img_url, headers=headers, timeout=10).content
				img = Image.open(BytesIO(img_data)).convert("RGB")
				images.append(img)
			except Exception:
				continue

		if not images:
			return None, 0, story_name

		pdf_buffer = BytesIO()
		images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=images[1:])
		pdf_buffer.seek(0)

		return pdf_buffer, len(images), story_name
