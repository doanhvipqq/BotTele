import os
import re
import yt_dlp
import tempfile

MAX_MB = 50

def safe_name(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def is_supported(url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'cachedir': False}) as ydl:
            ydl.extract_info(url, download=False)
            return True
    except:
        return False

def download(url, tmpdir):
    out = os.path.join(tmpdir, '%(title).50s.%(ext)s')
    opts = {
        'outtmpl': out,
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'cachedir': False
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
        safe_path = os.path.join(tmpdir, safe_name(os.path.basename(path)))
        if path != safe_path:
            os.rename(path, safe_path)
        return safe_path

def register_send(bot):
    @bot.message_handler(commands=['send'])
    def handle_send(message):
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) < 2:
            return bot.reply_to(message, "❗️ Vui lòng dùng đúng cú pháp:\n`/send <link>`", parse_mode="Markdown")

        url = parts[1].strip()
        msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        if not is_supported(url):
            return bot.edit_message_text(
                "🚫 Link không hợp lệ hoặc không được hỗ trợ.",
                msg.chat.id, msg.message_id
            )

        bot.edit_message_text("⏳ Đang tải video, vui lòng chờ...", msg.chat.id, msg.message_id)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = download(url, tmpdir)
                size_mb = os.path.getsize(video_path) / (1024 * 1024)

                if size_mb > MAX_MB:
                    return bot.edit_message_text(
                        f"🚫 File quá lớn ({size_mb:.1f}MB > {MAX_MB}MB), không thể gửi qua Telegram.",
                        msg.chat.id, msg.message_id
                    )

                with open(video_path, 'rb') as f:
                    bot.send_video(message.chat.id, f, reply_to_message_id=message.message_id)
                bot.delete_message(msg.chat.id, msg.message_id)

        except Exception as e:
            bot.edit_message_text(
                f"❌ Lỗi khi xử lý video:\n`{e}`",
                msg.chat.id, msg.message_id,
                parse_mode="Markdown"
            )
