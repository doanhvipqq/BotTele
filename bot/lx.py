import re
import zipfile
import requests
from io import BytesIO
from telebot import types
from bs4 import BeautifulSoup

# Lưu thông tin theo chat để tránh lẫn lộn
chat_data = {}

def get_name_manga(url):
	response = requests.get(url, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser")
	return soup.find("title").text.strip()

def get_cover(url):
	response = requests.get(url, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser")
	
	cover_div = soup.select_one(".cover")
	if not cover_div:
		return None
		
	style = cover_div.get("style", "")
	match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
	if not match:
		return None
		
	headers = {"Referer": url, "User-Agent": "Mozilla/5.0"}
	resp = requests.get(match.group(1), headers=headers, timeout=10)
	
	cover_file = BytesIO(resp.content)
	cover_file.name = "cover.jpg"
	return cover_file

def get_chapters_and_urls(url):
	response = requests.get(url, timeout=10)
	soup = BeautifulSoup(response.text, "html.parser")
	
	# Lấy tên chương
	chapters = []
	img_tags = soup.find_all("img", alt="untag-r")
	for img in img_tags:
		span = img.find_next("span")
		if span:
			chapters.append(span.get_text(strip=True))
	
	# Lấy URL chương  
	urls = []
	for a in soup.find_all("a", href=True):
		href = a.get("href", "")
		if href.startswith("/truyen/") and href.count("/") == 3:
			urls.append(f"https://lxmanga.blog{href}")
	
	return chapters, urls[1:] if urls else []

def get_chapter_images(chapter_url):
	headers = {"Referer": chapter_url, "User-Agent": "Mozilla/5.0"}
	response = requests.get(chapter_url, headers=headers, timeout=15)
	soup = BeautifulSoup(response.text, "html.parser")
	
	images = []
	for index, div in enumerate(soup.select("div.text-center div.lazy"), 1):
		img_url = div.get("data-src")
		if img_url:
			r = requests.get(img_url, headers=headers, timeout=10)
			img = BytesIO(r.content)
			img.name = f"{index:03}.jpg"
			images.append(img)
	return images

def create_chapter_zip(manga_name, chapter_title, chapter_url, cover_file=None):
	zip_buf = BytesIO()
	with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
		if cover_file:
			zipf.writestr(f"{manga_name}/cover.jpg", cover_file.getvalue())
		images = get_chapter_images(chapter_url)
		if not images:
			return None, "Không có ảnh"
			
		for i, img in enumerate(images, 1):
			path = f"{manga_name}/{chapter_title}/{i}.jpg"
			zipf.writestr(path, img.getvalue())

	zip_buf.seek(0, 2)
	if zip_buf.tell() > 50 * 1024 * 1024:
		return None, "File vượt quá 50MB, không thể gửi qua Telegram"
	
	zip_buf.seek(0)
	zip_buf.name = "lxm.zip"
	return zip_buf, None

def register_lx(bot):
	@bot.message_handler(commands=['lx'])
	def handle_manga_request(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2:
			bot.reply_to(message, "🚫 Nhập URL truyện cần tải.\nVí dụ: /lx https://lxmanga.blog/truyen/...")
			return

		url = args[1]
		chat_id = message.chat.id
		
		if not url.startswith("https://lxmanga.blog/"):
			bot.reply_to(message, "🚫 Chỉ hỗ trợ lxmanga.blog")
			return

		# Hiển thị đang xử lý
		processing_msg = bot.reply_to(message, "⏳ Đang tải thông tin truyện...")

		try:
			manga_name = get_name_manga(url)
			chapters, chapter_urls = get_chapters_and_urls(url)
			cover = get_cover(url)
			if not chapters:
				bot.edit_message_text("❌ Không tìm thấy chương nào!", 
									chat_id, processing_msg.message_id)
				return

			# Lưu data cho chat này
			chat_data[chat_id] = {
				'manga_name': manga_name,
				'chapters': chapters,
				'urls': chapter_urls,
				'manga_url': url,
				'cover': cover
			}

			# Tạo keyboard chọn chương
			markup = types.InlineKeyboardMarkup(row_width=3)
			
			# Tạo nút cho từng chương (đảo ngược để chương mới nhất ở trên)
			buttons = []
			for i in range(len(chapters)):
				buttons.append(types.InlineKeyboardButton(
					text=chapters[i], 
					callback_data=f"ch|{i}"
				))
			
			# Chia thành hàng 3 nút
			for i in range(0, len(buttons[::-1]), 3):  # Đảo ngược
				markup.row(*buttons[::-1][i:i+3])
			
			# Nút tải tất cả
			markup.add(types.InlineKeyboardButton("📦 Tải tất cả", callback_data="all"))

			# Gửi ảnh bìa + menu chọn
			bot.delete_message(chat_id, processing_msg.message_id)
			
			caption = f"📚 <b>{manga_name}</b>\n🔢 Có {len(chapters)} chương\n\n👇 Chọn chương cần tải:"
			
			if cover:
				bot.send_photo(chat_id, cover, caption=caption, reply_markup=markup)
			else:
				bot.send_message(chat_id, caption, reply_markup=markup)
				
		except Exception as e:
			bot.edit_message_text(f"❌ Lỗi: {e}", chat_id, processing_msg.message_id)

	# Xử lý khi chọn 1 chương
	@bot.callback_query_handler(func=lambda call: call.data.startswith("ch|"))
	def handle_single_chapter(call):
		chat_id = call.message.chat.id
		chapter_index = int(call.data.split("|")[1])
		
		if chat_id not in chat_data:
			bot.answer_callback_query(call.id, "❌ Hết hạn, thử lại!", show_alert=True)
			return
		
		data = chat_data[chat_id]
		chapter_title = data['chapters'][chapter_index]
		chapter_url = data['urls'][chapter_index]
		cover = data.get('cover')
		
		# Edit tin nhắn thành trạng thái đang tải
		bot.edit_message_caption(
			caption=f"📥 Đang tải: <b>{chapter_title}</b>...",
			chat_id=chat_id,
			message_id=call.message.message_id
		)
		bot.answer_callback_query(call.id)
		
		try:
			manga_name = data['manga_name']
			zip_file, error = create_chapter_zip(manga_name, chapter_title, chapter_url, cover)
			if error:
				bot.edit_message_caption(
					caption=f"❌ Lỗi tải chương: {error}",
					chat_id=chat_id,
					message_id=call.message.message_id
				)
				return
			
			# Edit thành hoàn thành và gửi file
			bot.edit_message_caption(
				caption=f"<b>{manga_name}</b>\n✅ Tải thành công <b>{chapter_title}</b>",
				chat_id=chat_id,
				message_id=call.message.message_id
			)
			
			bot.send_document(chat_id, zip_file, caption=f"📁 {chapter_title}")
			del chat_data[chat_id]

		except Exception as e:
			bot.edit_message_caption(
				caption=f"❌ Lỗi: {e}",
				chat_id=chat_id,
				message_id=call.message.message_id
			)

	# Xử lý tải tất cả chương
	@bot.callback_query_handler(func=lambda call: call.data == "all")
	def handle_all_chapters(call):
		chat_id = call.message.chat.id
		
		if chat_id not in chat_data:
			bot.answer_callback_query(call.id, "❌ Hết hạn, thử lại!", show_alert=True)
			return
		
		data = chat_data[chat_id]
		total = len(data['chapters'])
		
		# Edit tin nhắn thành trạng thái đang tải tất cả
		bot.edit_message_caption(
			caption=f"📦 Đang tải tất cả {total} chương...",
			chat_id=chat_id,
			message_id=call.message.message_id
		)
		bot.answer_callback_query(call.id)
		
		try:
			zip_buf = BytesIO()
			manga_name = data['manga_name']
			with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
				if data.get('cover'):
					zipf.writestr(f"{manga_name}/cover.jpg", data['cover'].getvalue())
					
				for i, (chapter_title, chapter_url) in enumerate(zip(data['chapters'][::-1], data['urls'][::-1])):
					# Update progress mỗi 3 chương
					if i % 3 == 0:
						progress = int((i + 1) / total * 100)
						try:
							bot.edit_message_caption(
								caption=f"📦 Đang tải... {i+1}/{total} ({progress}%)\n📖 {chapter_title}",
								chat_id=chat_id,
								message_id=call.message.message_id
							)
						except:
							pass
					
					# Tải ảnh chương
					images = get_chapter_images(chapter_url)
					for j, img in enumerate(images, 1):
						path = f"{data['manga_name']}/{chapter_title}/{j}.jpg"
						zipf.writestr(path, img.getvalue())

			zip_buf.seek(0, 2)  # Di chuyển tới cuối để đo dung lượng
			if zip_buf.tell() > 50 * 1024 * 1024:
				bot.edit_message_caption(
					caption="🚫 File toàn bộ chương vượt quá 50MB, không thể gửi qua Telegram!",
					chat_id=chat_id,
					message_id=call.message.message_id
				)
				return
			
			zip_buf.seek(0)
			zip_buf.name = "lxm.zip"
			
			# Edit thành hoàn thành
			bot.edit_message_caption(
				caption=f"<b>{manga_name}</b>\n✅ Đã tải thành công {total} chương!",
				chat_id=chat_id,
				message_id=call.message.message_id
			)
			
			bot.send_document(chat_id, zip_buf, caption=f"📦 {data['manga_name']} - Full")
			del chat_data[chat_id]
			
		except Exception as e:
			bot.edit_message_caption(
				caption=f"❌ Lỗi tải tất cả: {e}",
				chat_id=chat_id,
				message_id=call.message.message_id
			)
