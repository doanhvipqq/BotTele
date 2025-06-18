import os
import yt_dlp
import tempfile
from urllib.parse import urlparse

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
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def register_send(bot):
    @bot.message_handler(commands=['send'])
    def handle_send(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2 or not args[1].strip():
            return bot.reply_to(message, "❗️ Vui lòng dùng đúng cú pháp: /send <link>")

        url = args[1].strip()
        msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        if not is_url_supported(url):
            return bot.edit_message_text(
                "🚫 Nền tảng không được hỗ trợ hoặc link không hợp lệ.",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )

        bot.edit_message_text(
            "⏳ Đang tải video, vui lòng chờ...",
            chat_id=msg.chat.id,
            message_id=msg.message_id
        )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = download_video(url, tmpdir)
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

                if file_size_mb > 50:
                    bot.edit_message_text(
                        "🚫 File quá lớn (>50MB), không thể gửi qua Telegram.",
                        chat_id=msg.chat.id,
                        message_id=msg.message_id
                    )
                else:
                    with open(video_path, 'rb') as video_file:
                        bot.send_video(message.chat.id, video_file, reply_to_message_id=message.message_id)
                    bot.delete_message(msg.chat.id, msg.message_id)

        except Exception as e:
            bot.edit_message_text(
                f"❌ Lỗi khi xử lý video: {str(e)}",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )