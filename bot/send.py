import os
import yt_dlp
import tempfile

MAX_FILE_SIZE_MB = 50
MAX_SENDABLE_SIZE_MB = 2000  # Telegram tối đa cho bot gửi file là 2GB

# === HÀM KIỂM TRA LINK CÓ HỖ TRỢ HAY KHÔNG ===
def is_url_supported(url: str) -> bool:
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ydl.extract_info(url, download=False)
            return True
    except yt_dlp.utils.DownloadError:
        return False
    except Exception:
        return False

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

# === ĐĂNG KÝ LỆNH /send ===
def register_send(bot):
    @bot.message_handler(commands=['send'])
    def handle_send(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❗ Vui lòng dùng đúng cú pháp: /send <link>")
            return

        url = args[1]

        # Gửi phản hồi trung gian trước khi kiểm tra URL
        msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        if not is_url_supported(url):
            bot.edit_message_text(
                "🚫 Nền tảng không được hỗ trợ hoặc link không hợp lệ.",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )
            return

        # Gửi thông báo tiếp theo trước khi bắt đầu tải
        bot.edit_message_text(
            "⏳ Đang tải video, vui lòng chờ...",
            chat_id=msg.chat.id,
            message_id=msg.message_id
        )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = download_video(url, tmpdir)
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

                # Nếu vượt quá giới hạn Telegram cho phép
                if file_size_mb > MAX_SENDABLE_SIZE_MB:
                    bot.edit_message_text(
                        "🚫 Video quá lớn (>2GB), Telegram không cho phép gửi file này.",
                        chat_id=msg.chat.id,
                        message_id=msg.message_id
                    )
                    return

                with open(video_path, 'rb') as video_file:
                    if file_size_mb > MAX_FILE_SIZE_MB:
                        bot.send_document(
                            chat_id=message.chat.id,
                            document=video_file,
                            caption="📦 Video lớn được gửi dưới dạng tài liệu",
                            reply_to_message_id=message.message_id
                        )
                    else:
                        bot.send_video(
                            chat_id=message.chat.id,
                            video=video_file,
                            reply_to_message_id=message.message_id
                        )

                # Xoá tin nhắn "đang xử lý"
                bot.delete_message(msg.chat.id, msg.message_id)

        except Exception as e:
            bot.edit_message_text(
                f"❌ Lỗi khi xử lý video: {str(e)}",
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )