import random
from config import ADMIN_ID, ERROR_MSG

MAX_ATTEMPTS = 5

def send_random_media(bot, message, file_path, media_type):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Lỗi: {e}")
        return bot.reply_to(message, ERROR_MSG)

    if not urls:
        return bot.reply_to(message, "Danh sách chưa có dữ liệu!")

    random.shuffle(urls)

    send_func = {
        "photo": bot.send_photo,
        "video": bot.send_video,
        "animation": bot.send_animation,
    }.get(media_type)

    if not send_func:
        bot.send_message(ADMIN_ID, f"⚠️ Lệnh /{message.text} có media_type không hợp lệ: {media_type}")
        return bot.reply_to(message, ERROR_MSG)
        
    for attempts, url in enumerate(urls[:MAX_ATTEMPTS]):
        try:
            send_func(message.chat.id, url, reply_to_message_id=message.message_id)
            return
        except Exception as e:
            bot.send_message(
                ADMIN_ID,
                f"⚠️ Lỗi gửi {media_type} từ lệnh /{message.text}:\nURL: {url}\nLỗi: {e}"
            )

    bot.reply_to(message, ERROR_MSG)



COMMANDS = {
    "anime": {
        "path": "bot/url/anime.txt",
        "type": "video"
    },
    "girl": {
        "path": "bot/url/girl.txt",
        "type": "video"
    },
    "imganime": {
        "path": "bot/url/imganime.txt",
        "type": "photo"
    }
}


def create_handler(bot, path, mtype):
    def handler(message):
        send_random_media(bot, message, path, mtype)
    return handler

def register_random(bot):
    for cmd, cfg in COMMANDS.items():
        handler = create_handler(bot, cfg["path"], cfg["type"])
        bot.register_message_handler(handler, commands=[cmd])
