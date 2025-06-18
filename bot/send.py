import os
import re
import yt_dlp
import tempfile

MAX_MB = 50

def safe_name(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def is_supported(url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
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
        'merge_output_format': 'mp4'
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
    def handle_send(msg):
        parts = msg.text.strip().split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return bot.reply_to(msg, "❗️ Dùng đúng cú pháp: /send <link>")

        url = parts[1].strip()
        notice = bot.reply_to(msg, "🔍 Đang xử lý...")

        if not is_supported(url):
            return bot.edit_message_text("🚫 Link không hợp lệ hoặc không hỗ trợ.",
                                         notice.chat.id, notice.message_id)

        bot.edit_message_text("⏳ Đang tải video...", notice.chat.id, notice.message_id)

        try:
            with tempfile.TemporaryDirectory() as tmp:
                path = download(url, tmp)
                size = os.path.getsize(path) / 1024 / 1024
                if size > MAX_MB:
                    bot.edit_message_text("🚫 File quá lớn (>50MB).", notice.chat.id, notice.message_id)
                else:
                    with open(path, 'rb') as f:
                        bot.send_video(msg.chat.id, f, reply_to_message_id=msg.message_id)
                    bot.delete_message(notice.chat.id, notice.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi: {e}", notice.chat.id, notice.message_id)