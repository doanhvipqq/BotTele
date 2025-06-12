import random

# Hàm gửi media ngẫu nhiên từ file
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
            send_func(message.chat.id, **{media_type: url}, reply_to_message_id=message.message_id)
        else:
            bot.reply_to(message, "Không xác định kiểu media!")
    except Exception as e:
        bot.reply_to(message, f"Lỗi: {e}")

# Danh sách lệnh và file tương ứng
COMMANDS = [
    ("anime",     "bot/url/anime",     "video"),
    ("girl",      "bot/url/girl",      "video"),
    ("imganime",  "bot/url/imganime",  "photo"),
    ("butt",      "bot/url/butt",      "photo"),
    ("squeeze",   "bot/url/squeeze",   "animation"),
    ("cosplay",   "bot/url/cosplay",   "photo"),
    ("pussy",     "bot/url/pussy",     "photo"),
    ("nude",      "bot/url/nude",      "photo"),
    ("girlsexy",  "bot/url/girlsexy",  "photo"),
]

def register_random(bot):
    for command, path, media_type in COMMANDS:
        @bot.message_handler(commands=[command])
        def handler(message, path=path, mtype=media_type):
            send_random_media(bot, message, path, mtype)