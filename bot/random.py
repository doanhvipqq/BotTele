import random

# Hàm xử lý chung
def handle_media(bot, message, file_path, media_type):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
        
        if not urls:
            bot.reply_to(message, "Danh sách chưa có dữ liệu!")
            return
        
        selected = random.choice(urls)

        send_func = {
            "photo": bot.send_photo,
            "video": bot.send_video,
            "animation": bot.send_animation
        }.get(media_type)

        if send_func:
            send_func(chat_id=message.chat.id, **{media_type: selected}, reply_to_message_id=message.message_id)
        else:
            bot.reply_to(message, "Không xác định kiểu media!")
    except Exception as e:
        bot.reply_to(message, f"Lỗi: {e}")

# Danh sách lệnh và đường dẫn tương ứng
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

# Đăng ký handler tự động
def register_random(bot):
    for command, path, media_type in COMMANDS:
        def create_handler(file_path=path, media_type=media_type):  # cần default arg để tránh late binding
            @bot.message_handler(commands=[command])
            def handler(message):
                handle_media(bot, message, file_path, media_type)
            return handler

        create_handler()  # Gọi để tạo và đăng ký