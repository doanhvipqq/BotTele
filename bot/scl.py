import io
import os
import re
import json
import requests
import threading
from telebot import types

API_BASE = "https://api-v2.soundcloud.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CONFIG_PATH = "config.json"

scl_data = {}

def get_client_id():
	if os.path.exists(CONFIG_PATH):
	        with open(CONFIG_PATH, 'r') as f:
	            config = json.load(f)
	        if config.get('client_id'):
	            return config['client_id']


	# Nếu chưa có trong config, fetch script để lấy
	try:
		resp = requests.get("https://soundcloud.com/", headers=HEADERS)
		resp.raise_for_status()
		urls = re.findall(r'<script crossorigin src="(https[^"]+)"', resp.text)
		script = requests.get(urls[-1], headers=HEADERS).text
		cid = re.search(r',client_id:"([^"]+)"', script).group(1)
		
		with open(CONFIG_PATH, 'w') as f:
			json.dump({"client_id": cid}, f, indent=2)
		return cid
	except Exception:
		return "vjvE4M9RytEg9W09NH1ge2VyrZPUSKo5"

def get_music_info(question, limit=20):
	try:
		client_id = get_client_id()
		response = requests.get(
			f"{API_BASE}/search/tracks",
			params={
				"q": question,
				"client_id": client_id,
				"limit": limit
			},
			headers=HEADERS
		)
		response.raise_for_status()
		return response.json()
	except Exception:
		return None

def get_music_stream_url(track):
	client_id = get_client_id()  # thêm dòng này
	transcodings = track.get("media", {}).get("transcodings", [])
	for item in transcodings:
		if item["format"]["protocol"] == "progressive":
			stream_api = item["url"] + f"?client_id={client_id}"
			resp = requests.get(stream_api)
			if resp.status_code == 200:
				return resp.json().get("url")
	return None
	
def register_scl(bot):
	@bot.message_handler(commands=['scl'])
	def soundcloud(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2:
			bot.reply_to(message, "🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /scl Lệ cay 3")
			return

		keyword = args[1]
		music_info = get_music_info(keyword)

		collection = music_info.get("collection") if music_info else None
		if not collection:
			bot.reply_to(message, "🚫 Không tìm thấy bài hát nào khớp với từ khóa.")
			return

		tracks = [t for t in music_info['collection'] if t.get("artwork_url")]
		tracks = tracks[:10]
		if not tracks:
			bot.reply_to(message, "🚫 Không tìm thấy bài hát nào có hình ảnh.")
			return

		# Tạo response text
		lines = ["<b>🎵 Kết quả tìm kiếm trên SoundCloud</b>\n"]
		for i, track in enumerate(tracks):
			lines.append(
				f"<b>{i + 1}. {track['title']}</b>\n"
				f" <b>» Nghệ sĩ:</b> {track['user']['username']}\n"
				f" <b>» Lượt nghe:</b> {track['playback_count']:,} | <b>Thích:</b> {track['likes_count']:,}\n"
			)
		lines.append("<b>💡 Chọn số bài hát bạn muốn tải!</b>")
		response_text = "\n".join(lines)

		# Tạo inline keyboard
		markup = types.InlineKeyboardMarkup(row_width=5)
		markup.add(*[
			types.InlineKeyboardButton(str(i + 1), callback_data=f"scl_{message.from_user.id}_{i}")
			for i in range(len(tracks))
		])

		# Gửi message với inline keyboard
		sent = bot.reply_to(message, response_text, reply_markup=markup)
		# Lưu data cho callback
		key = f"{message.from_user.id}_{sent.message_id}"
		scl_data[key] = {
			"tracks": tracks,
			"chat_id": sent.chat.id,
			"command_msg_id": message.message_id,
		}

		# Tự động xóa sau 2 phút nếu chưa chọn
		def delete_if_not_used():
			if key in scl_data:
				try:
					bot.delete_message(sent.chat.id, sent.message_id)
					bot.delete_message(sent.chat.id, scl_data[key]["command_msg_id"])
				except:
					pass
				scl_data.pop(key, None)

		threading.Timer(120, delete_if_not_used).start()

	@bot.callback_query_handler(func=lambda call: call.data.startswith('scl_'))
	def handle_soundcloud_callback(call):
		try:
			# Parse callback data
			parts = call.data.split('_')
			user_id = int(parts[1])
			track_index = int(parts[2])
			
			# Kiểm tra quyền truy cập
			if call.from_user.id != user_id:
				bot.answer_callback_query(call.id, "❌ Bạn không có quyền sử dụng nút này!", show_alert=True)
				return
			
			key = f"{user_id}_{call.message.message_id}"
			data = scl_data.pop(key, None)
			if not data:
				bot.answer_callback_query(call.id, "❌ Dữ liệu đã hết hạn hoặc đã dùng rồi!", show_alert=True)
				return
				
			tracks = data["tracks"]
			# Kiểm tra index hợp lệ
			if track_index >= len(tracks):
				bot.answer_callback_query(call.id, "❌ Lựa chọn không hợp lệ!", show_alert=True)
				return
			
			track = tracks[track_index]
			bot.answer_callback_query(call.id, f"🎵 Đang tải: {track['title']}")
			bot.edit_message_text(
				f"🧭 Đang tải: <b>{track['title']}</b>\n👤 Nghệ sĩ: {track['user']['username']}\n\n⏳ Vui lòng chờ...",
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
			)
			
			# Lấy audio URL và thumbnail
			audio_url = get_music_stream_url(track)
			thumbnail_url = track.get('artwork_url', '').replace("-large", "-t500x500")
			if not audio_url or not thumbnail_url:
				bot.edit_message_text(
					"🚫 Không tìm thấy nguồn audio hoặc thumbnail.",
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
				)
				return
			
			caption = f"""<blockquote>⭔───────────────⭓
 <b>{track['title']}</b>
 » <b>Nghệ sĩ:</b> {track['user']['username']}
 » <b>Lượt nghe:</b> {track['playback_count']:,}
 » <b>Lượt thích:</b> {track['likes_count']:,}
 » <b>Nguồn:</b> SoundCloud 🎶 
⭓───────────────⭔</blockquote>"""
			
			resp = requests.get(audio_url, stream=True)
			resp.raise_for_status()

			content_length = int(resp.headers.get('Content-Length', 0))
			if content_length > 50 * 1024 * 1024:  # Giới hạn 50MB
				bot.edit_message_text(
					"🚫 File nhạc quá lớn (>50MB) nên không thể gửi qua Telegram.",
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
				)
				return

			audio = io.BytesIO(resp.content)
			audio.name = f"{track['title']}.mp3"
			
			# Gửi ảnh thumbnail và audio
			bot.send_photo(call.message.chat.id, thumbnail_url, caption=caption)
			bot.send_audio(
				call.message.chat.id,
				audio,
				title=track['title'],
				performer=track['user']['username']
			)
			
			# Xóa tin nhắn kết quả tìm kiếm
			try:
				bot.delete_message(call.message.chat.id, call.message.message_id)
			except Exception:
				pass

		except Exception as e:
			bot.answer_callback_query(call.id, f"❌ Có lỗi xảy ra: {str(e)}", show_alert=True)
