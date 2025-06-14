import os
import tempfile
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

MAX_FILE_SIZE_MB = 50
pending_urls = {}  # user_id -> url

def is_url_supported(url: str) -> bool:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ydl.extract_info(url, download=False)
            return True
    except:
        return False

def download_video(url: str, tmpdir: str) -> str:
    output_template = os.path.join(tmpdir, '%(title).50s.%(ext)s')
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def download_audio(url: str, tmpdir: str) -> str:
    output_template = os.path.join(tmpdir, '%(title).50s.%(ext)s')
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

def register_send(bot):
    @bot.message_handler(commands=['send'])
    def handle_send(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❗ Dùng đúng cú pháp: /send <link>")
            return

        url = args[1]
        if not is_url_supported(url):
            bot.reply_to(message, "🚫 Link không hợp lệ hoặc không hỗ trợ.")
            return

        # Lưu URL tạm thời theo user_id
        pending_urls[message.from_user.id] = url

        # Gửi nút chọn
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("🎬 Tải Video", callback_data="download_video"),
            InlineKeyboardButton("🎵 Tải Audio", callback_data="download_audio")
        )
        bot.reply_to(message, "🔽 Chọn định dạng bạn muốn tải:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data in ['download_video', 'download_audio'])
    def handle_download(call):
        user_id = call.from_user.id
        url = pending_urls.get(user_id)

        if not url:
            bot.answer_callback_query(call.id, "❌ Không tìm thấy URL. Vui lòng dùng lại lệnh /send.")
            return

        bot.edit_message_text("⏳ Đang tải, vui lòng chờ...",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                if call.data == 'download_video':
                    file_path = download_video(url, tmpdir)
                    file_type = 'video'
                else:
                    file_path = download_audio(url, tmpdir)
                    file_type = 'audio'

                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE_MB:
                    bot.edit_message_text("🚫 File quá lớn (>50MB), không thể gửi qua Telegram.",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id)
                else:
                    with open(file_path, 'rb') as f:
                        if file_type == 'video':
                            bot.send_video(call.message.chat.id, f, reply_to_message_id=call.message.message_id)
                        else:
                            bot.send_audio(call.message.chat.id, f, reply_to_message_id=call.message.message_id)
                    bot.delete_message(call.message.chat.id, call.message.message_id)

        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi khi xử lý: {str(e)}",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)

        # Xóa URL đã xử lý
        pending_urls.pop(user_id, None)
