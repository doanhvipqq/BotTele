import os
import yt_dlp
import tempfile
# Thêm import này
from urllib.parse import urlparse

# Cấu hình yt-dlp
def get_ydl_opts(output_path):
    return {
        'format': 'best[height<=720]/best',  # Giới hạn chất lượng để tránh file quá lớn
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }

def is_supported(url): # Kiểm tra URL có hợp lệ không
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def download_video(url, temp_dir):
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts(temp_dir)) as ydl:
            # Lấy thông tin video
            ydl.extract_info(url, download=True)

            for file in os.listdir(temp_dir):
                if file.endswith(('.mp4', '.mkv', '.webm', '.avi', '.mov')):
                    return os.path.join(temp_dir, file)
            return None
    except Exception:
        return None

def register_send(bot):
    @bot.message_handler(commands=['send'])
    def handle_send(message):
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng cung cấp URL video muốn tải. \n Ví dụ: /send https://youtube.com/watch?v=abc123")
            return
        
        url = args[1].strip()
        
        # Kiểm tra URL hợp lệ
        if not is_supported(url):
            bot.reply_to(message, "🚫 Nền tảng không được hỗ trợ hoặc link không hợp lệ.")
            return

        msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                video_file_path = download_video(url, temp_dir)
                if video_file_path:
                    file_size = os.path.getsize(video_file_path)
                    if file_size <= 50 * 1024 * 1024: # 50MB
                        with open(video_file_path, 'rb') as video_file:
                            bot.send_video(message.chat.id, video_file, reply_to_message_id=message.message_id)
                        bot.delete_message(msg.chat.id, msg.message_id)
                    else:
                        
                        bot.edit_message_text(
                            f"🚫 File quá lớn (>50MB), không thể gửi qua Telegram.",
                            msg.chat.id, msg.message_id
                        )
                else:
                    bot.edit_message_text(
                        "❌ Không thể tải video. Vui lòng kiểm tra lại URL.",
                        msg.chat.id, msg.message_id
                    )

            except Exception as e:
                bot.edit_message_text(
                    f"❌ Lỗi khi xử lý video: {e}",
                    msg.chat.id, msg.message_id
                )
