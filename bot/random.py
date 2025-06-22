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
        
    attempts = 0
    for url in urls: # 5 lần thử lại
        if attempts >= 5:
            break
        try:
            send_func(message.chat.id, url, reply_to_message_id=message.message_id)
            return
        except Exception as e:
            attempts += 1
            bot.send_message(ADMIN_ID, f"⚠️ Lỗi gửi {media_type} từ lệnh /{message.text}:\nURL: {url}\nLỗi: {e}")

    bot.reply_to(message, "Tất cả URL đều lỗi, vui lòng thử lại sau.")


COMMANDS = [
    {"command": "anime", "path": "bot/url/anime.txt", "type": "video"},
    {"command": "girl", "path": "bot/url/girl.txt", "type": "video"},
    {"command": "imganime", "path": "bot/url/imganime.txt", "type": "photo"},
    {"command": "butt", "path": "bot/url/butt.txt", "type": "photo"},
    {"command": "cosplay", "path": "bot/url/cosplay.txt", "type": "photo"},
    {"command": "pussy", "path": "bot/url/pussy.txt", "type": "photo"},
    {"command": "nude", "path": "bot/url/nude.txt", "type": "photo"},
    {"command": "girlsexy", "path": "bot/url/girlsexy.txt", "type": "photo"},
    {"command": "squeeze", "path": "bot/url/squeeze.txt", "type": "animation"},
]

def create_handler(bot, path, mtype):
    def handler(message):
        send_random_media(bot, message, path, mtype)
    return handler

def register_random(bot):
    for cmd in COMMANDS:
        handler = create_handler(bot, cmd["path"], cmd["type"])  # sửa ở đây
        bot.register_message_handler(handler, commands=[cmd["command"]])