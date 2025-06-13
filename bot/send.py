import os
import tempfile
import yt_dlp

MAX_FILE_SIZE_MB = 50

# === HÀM TẢI VIDEO ===
def download_video(url: str, tmpdir: str) -> str:
    """Tải video từ mạng xã hội vào thư mục tạm, trả về đường dẫn file."""
    output_template = os.path.join(tmpdir, '%(title).50s.%(ext)s')
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'format': 'mp4/bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def register_send(bot):
    # === XỬ LÝ LỆNH /send <url> ===
    @bot.message_handler(commands=['send'])
    def handle_send(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❗ Vui lòng dùng đúng cú pháp: /send <link>")
            return
    
        url = args[1]
        msg = bot.reply_to(message, "⏳ Đang tải video, vui lòng chờ...")
    
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = download_video(url, tmpdir)
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    
                if file_size_mb > MAX_FILE_SIZE_MB:
                    bot.edit_message_text(
                        "🚫 File quá lớn (>50MB), không thể gửi qua Telegram.",
                        chat_id=msg.chat.id,
                        message_id=msg.message_id
                    )
                else:
                    with open(video_path, 'rb') as video_file:
                        bot.send_video(message.chat.id, video_file)
                    bot.delete_message(msg.chat.id, msg.message_id)
    
        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi: {str(e)}", chat_id=msg.chat.id, message_id=msg.message_id)
    
    
