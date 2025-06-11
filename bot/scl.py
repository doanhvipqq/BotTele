import io
import os
import re
import json
import requests
from telebot import types

scl_data = {}
API_BASE = "https://api-v2.soundcloud.com"
CONFIG_PATH = "config.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def get_client_id():
    # Đọc config sẵn
    config = {}
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
    except Exception as e:
        print(f"[ERROR] Lấy client_id thất bại: {e}")
        return "vjvE4M9RytEg9W09NH1ge2VyrZPUSKo5"

def get_music_info(question, limit=10):
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
    except Exception as e:
        print(f"Error fetching music info: {e}")
        return None

def get_music_stream_url(track):
    try:
        client_id = get_client_id()
        api_url = f"{API_BASE}/resolve?url={track['permalink_url']}&client_id={client_id}"
        response = requests.get(api_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        progressive_url = next(
            (t['url'] for t in data.get('media', {}).get('transcodings', []) if t['format']['protocol'] == 'progressive'),
            None
        )
        if not progressive_url:
            raise ValueError("No progressive transcoding URL found")
        stream_response = requests.get(
            f"{progressive_url}?client_id={client_id}",
            headers=HEADERS
        )
        stream_response.raise_for_status()
        return stream_response.json()['url']
    except Exception as e:
        print(f"Error getting music stream URL: {e}")
        return None

def register_scl(bot):
    @bot.message_handler(commands=['scl'])
    def soundcloud(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(
                message,
                "🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /scl Tên bài hát",
                parse_mode='HTML'
            )
            return

        keyword = args[1].strip()
        music_info = get_music_info(keyword)
        if not music_info or not music_info.get('collection') or len(music_info['collection']) == 0:
            bot.reply_to(
                message,
                "🚫 Không tìm thấy bài hát nào khớp với từ khóa.",
                parse_mode='HTML'
            )
            return

        tracks = [track for track in music_info['collection'] if track.get('artwork_url')]
        if not tracks:
            bot.reply_to(
                message,
                "🚫 Không tìm thấy bài hát nào có hình ảnh.",
                parse_mode='HTML'
            )
            return

        # Tạo response text
        lines = ["<b>🎵 Kết quả tìm kiếm trên SoundCloud</b>\n"]
        for i, track in enumerate(tracks):
            lines.append(f"<b>{i + 1}. {track['title']}</b>")
            lines.append(f"👤 Nghệ sĩ: {track['user']['username']}")
            lines.append(f"📊 Lượt nghe: {track['playback_count']:,} | Thích: {track['likes_count']:,}\n")
        lines.append("<b>💡 Chọn số bài hát bạn muốn tải!</b>")
        response_text = "\n".join(lines)

        # Tạo inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons = []
        for i in range(len(tracks)):
            button = types.InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"scl_{message.from_user.id}_{i}"
            )
            buttons.append(button)
        markup.add(*buttons)

        # Gửi message với inline keyboard
        sent = bot.reply_to(
            message,
            response_text,
            parse_mode='HTML',
            reply_markup=markup
        )
        # Lưu data cho callback
        scl_data[str(message.from_user.id)] = {
            "tracks": tracks,
            "message_id": sent.message_id,
        }

    @bot.callback_query_handler(func=lambda call: call.data.startswith('scl_'))
    def handle_soundcloud_callback(call):
        try:
            # Parse callback data
            parts = call.data.split('_')
            user_id = int(parts[1])
            track_index = int(parts[2])
            
            # Kiểm tra quyền truy cập
            if call.from_user.id != user_id:
                bot.answer_callback_query(
                    call.id,
                    "❌ Bạn không có quyền sử dụng nút này!",
                    show_alert=True
                )
                return
            
            data = scl_data.pop(str(user_id), None)
            if not data:
                bot.answer_callback_query(
                    call.id,
                    "❌ Dữ liệu đã hết hạn hoặc đã dùng rồi!",
                    show_alert=True
                )
                return
            tracks = data["tracks"]
            
            # Kiểm tra index hợp lệ
            if track_index >= len(tracks):
                bot.answer_callback_query(
                    call.id,
                    "❌ Lựa chọn không hợp lệ!",
                    show_alert=True
                )
                return
            
            track = tracks[track_index]
            # Answer callback query
            bot.answer_callback_query(call.id, f"🎵 Đang tải: {track['title']}")
            # Edit message để hiển thị loading
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🧭 Đang tải: <b>{track['title']}</b>\n👤 Nghệ sĩ: {track['user']['username']}\n\n⏳ Vui lòng chờ...",
                parse_mode='HTML'
            )
            
            # Lấy audio URL và thumbnail
            audio_url = get_music_stream_url(track)
            thumbnail_url = track.get('artwork_url', '').replace("-large", "-t500x500")
            if not audio_url or not thumbnail_url:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="🚫 Không tìm thấy nguồn audio hoặc thumbnail.",
                    parse_mode='HTML'
                )
                return
            
            caption = f"""<blockquote>⭔───────────────⭓
 <b>{track['title']}</b>
 » <b>Nghệ sĩ:</b> {track['user']['username']}
 » <b>Lượt nghe:</b> {track['playback_count']:,} | <b>Lượt thích:</b> {track['likes_count']:,}
 » <b>Nguồn:</b> SoundCloud 🎶 
⭓───────────────⭔</blockquote>"""
            
            # Tải audio về buffer và gửi về user
            try:
                resp = requests.get(audio_url, stream=True)
                resp.raise_for_status()
                audio_bytes = resp.content
                audio_buffer = io.BytesIO(audio_bytes)
                audio_buffer.name = f"{track['title']}.mp3"
                
                # Gửi ảnh thumbnail và audio
                bot.send_photo(
                    call.message.chat.id,
                    thumbnail_url,
                    caption=caption,
                    parse_mode='HTML'
                )
                bot.send_audio(
                    chat_id=call.message.chat.id,
                    audio=audio_buffer,
                    title=track['title'],
                    performer=track['user']['username']
                )
                
                # Xóa tin nhắn kết quả tìm kiếm
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass

            except Exception as e:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"🚫 Lỗi khi tải nhạc: {str(e)}",
                    parse_mode='HTML'
                )
        except Exception as e:
            bot.answer_callback_query(
                call.id,
                f"❌ Có lỗi xảy ra: {str(e)}",
                show_alert=True
            )
            print(f"Error in callback handler: {e}")
