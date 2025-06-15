import random
from config import ADMIN_ID

def send_random_media(bot, message, file_path, media_type):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return bot.reply_to(message, "File dữ liệu không tồn tại!")
    except Exception as e:
        return bot.reply_to(message, f"Lỗi khi đọc file: {e}")

    if not urls:
        return bot.reply_to(message, "Danh sách chưa có dữ liệu!")

    random.shuffle(urls)

    send_funcs = {
        "photo": bot.send_photo,
        "video": bot.send_video,
        "animation": bot.send_animation,
    }

    send_func = send_funcs.get(media_type)
    if not send_func:
        return bot.reply_to(message, "Không xác định kiểu media!")

    for url in urls:
        try:
            send_func(message.chat.id, url, reply_to_message_id=message.message_id)
            return
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Lỗi với URL:\n{url}\n👉 {e}")

    bot.reply_to(message, "Tất cả URL đều lỗi, vui lòng thử lại sau.")


COMMANDS = [
    ("anime", "bot/url/anime.txt", "video"),
    ("girl",  "bot/url/girl.txt",  "video"),
    ("imganime",  "bot/url/imganime.txt",  "photo"),
    ("butt",      "bot/url/butt.txt",      "photo"),
    ("cosplay",   "bot/url/cosplay.txt",   "photo"),
    ("pussy",     "bot/url/pussy.txt",     "photo"),
    ("nude",      "bot/url/nude.txt",      "photo"),
    ("girlsexy",  "bot/url/girlsexy.txt",  "photo"),
    ("squeeze", "bot/url/squeeze.txt", "animation"),
]

def create_handler(bot, path, mtype):
    def handler(message):
        send_random_media(bot, message, path, mtype)
    return handler

def register_random(bot):
    for command, path, media_type in COMMANDS:
        handler = create_handler(bot, path, media_type)
        bot.register_message_handler(handler, commands=[command])