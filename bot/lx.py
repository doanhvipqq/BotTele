import re
import telebot
import requests
from io import BytesIO
from telebot import types
from bs4 import BeautifulSoup

user_chapter_urls = {}





import zipfile
from urllib.parse import urlparse
from telebot.types import InputFile

def clean_filename(name):
	return re.sub(r'[\\/*?:"<>|]', " ", name).strip()

def get_zip_from_chapter(chap_url):
	headers = {
		"Referer": chap_url,
		"User-Agent": "Mozilla/5.0",
	}
	response = requests.get(chap_url, headers=headers, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser")

	a_tag = soup.find("a", class_="text-ellipsis font-semibold hover:text-blue-500")
	story_name = a_tag.get_text(strip=True) if a_tag else "Unknown"

	img_divs = soup.select("div.text-center div.lazy")
	img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]

	zip_buffer = BytesIO()
	with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
		for idx, img_url in enumerate(img_urls):
			try:
				ext = urlparse(img_url).path.split(".")[-1].split("?")[0] or "jpg"
				filename = f"{idx + 1}.{ext}"
				zip_path = f"{clean_filename(story_name)}/{filename}"
				img_data = requests.get(img_url, headers=headers, timeout=10).content
				zipf.writestr(zip_path, img_data)
			except Exception:
				continue

	zip_buffer.seek(0)
	return zip_buffer, len(img_urls), story_name





def get_name_manga(manga_url):
	response = requests.get(manga_url, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser")

	title_tag = soup.find("title")
	name_manga = title_tag.text
	# print(name_manga)
	return name_manga

def get_cover(manga_url):
	try:
		response = requests.get(manga_url, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		div_tags = soup.select_one(".cover")
		if not div_tags:
			return "Lỗi: Không tìm thấy thẻ .cover"

		style = div_tags.get("style", "")
		image_url = re.search(r"url\(['\"]?(.*?)['\"]?\)", style).group(1)
		if not image_url:
			return "Lỗi: Không tìm thấy URL trong style"
		# print(image_url)

		headers = {
			"Referer": manga_url,
			"User-Agent": "Mozilla/5.0"
		}
		resp = requests.get(image_url, headers=headers, timeout=10)
		resp.raise_for_status()
		cover_file = BytesIO(resp.content)
		cover_file.name = "cover.jpg"
		return cover_file

	except Exception as e:
		return

def get_chapters(manga_url):
	try:
		response = requests.get(manga_url, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		img_tags = soup.find_all("img", alt="untag-r")
		chapters = []
		# img_tags.reverse()
		for a in img_tags:
			ct = a.find_next("span")
			chapters.append(ct.get_text(strip=True))
		return chapters	#  print(chapters)

	except Exception as e:
		return [f"Lỗi: {e}"]

def get_chapter_urls(manga_url):
	try:
		response = requests.get(manga_url, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		a_tags = soup.find_all("a", href=True)
		# found_first = False
		urls = []

		for a in a_tags:
			href = a.get("href", "")
			if href.startswith("/truyen/") and href.count("/") == 3:
				# if not found_first:
				# 	found_first = True
				# 	continue
				urls.append(f"https://lxmanga.blog{href}")
				# print(url)
		return urls[1:]

	except Exception as e:
		return [f"Lỗi: {e}"]  

def register_lx(bot):
	@bot.message_handler(commands=['lx'])
	def handler_lx(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2:
			bot.reply_to(message, "🚫 Vui lòng url truyen can tai")
			return

		manga_url = args[1]
		sent_msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

		chapters = get_chapters(manga_url)
		chapter_urls = get_chapter_urls(manga_url)
		name_manga = get_name_manga(manga_url)

		# Tạo inline keyboard
		markup = types.InlineKeyboardMarkup(row_width=3)
		count = min(len(chapters), len(chapter_urls))
		buttons = [
			types.InlineKeyboardButton(text=chapters[i], callback_data=f"lx_{message.chat.id}_{message.message_id}_{i}")
			for i in reversed(range(count))
		]

		markup.add(*buttons)

		cover = get_cover(manga_url)
		try:
			user_chapter_urls[(message.chat.id, message.message_id)] = manga_url

			bot.send_photo(message.chat.id, cover, name_manga, reply_markup=markup)
		except Exception as e:
			bot.send_message(message.chat.id, f"⚠️ Không gửi được ảnh bìa:\n{e}")

	@bot.callback_query_handler(func=lambda call: call.data.startswith("lx_"))
	def handle_chapter_download(call):
		try:
			_, chat_id, msg_id, idx = call.data.split("_")
			chat_id = int(chat_id)
			msg_id = int(msg_id)
			idx = int(idx)

			# Lấy lại URL và gọi get_zip_from_chapter
			manga_url = user_chapter_urls.get((chat_id, msg_id))
			if not manga_url:
				return bot.answer_callback_query(call.id, "❌ Hết hạn hoặc không tìm thấy chương.")

			chapter_urls = get_chapter_urls(manga_url)
			chapter_url = chapter_urls[::-1][idx]

			zip_data, total, story_name = get_zip_from_chapter(chapter_url)
			if total == 0:
				return bot.answer_callback_query(call.id, "❌ Không tìm thấy ảnh nào.")

			filename = clean_filename(story_name) + ".zip"
			bot.send_document(
				call.message.chat.id,
				document=InputFile(zip_data, filename),
				caption=f"📦 {total} ảnh từ:\n<b>{story_name}</b>",
				parse_mode="HTML"
			)
			bot.answer_callback_query(call.id)
		except Exception as e:
			bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)}", show_alert=True)
