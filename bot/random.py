import random

def send_random_media(bot, message, file_path, media_type):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]

        if not urls:
            return bot.reply_to(message, "Danh sách chưa có dữ liệu!")

        url = random.choice(urls)

        send_funcs = {
            "photo": bot.send_photo,
            "video": bot.send_video,
            "animation": bot.send_animation,
        }

        send_func = send_funcs.get(media_type)
        if send_func:
            send_func(message.chat.id, url, reply_to_message_id=message.message_id)
        else:
            bot.reply_to(message, "Không xác định kiểu media!")
    except Exception as e:
        bot.reply_to(message, f"Lỗi: {e}")


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