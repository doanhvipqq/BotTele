import random

def register_anime(bot):
    @bot.message_handler(commands=['anime'])
    def handle_anime(message):
        try:
            file_path = "bot/url/anime"
            with open(file_path, "r", encoding="utf-8") as file:
                video_urls = [line.strip() for line in file if line.strip()]
            
            if not video_urls:
                bot.reply_to(message, "Danh sách video chưa có dữ liệu!")
                return

            selected_video = random.choice(video_urls)
            bot.send_video(chat_id=message.chat.id, video=selected_video, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_girl(bot):
    @bot.message_handler(commands=['girl'])
    def handle_girl(message):
        try:
            file_path = "bot/url/girl"
            with open(file_path, "r", encoding="utf-8") as file:
                video_urls = [line.strip() for line in file if line.strip()]
            
            if not video_urls:
                bot.reply_to(message, "Danh sách video chưa có dữ liệu!")
                return

            selected_video = random.choice(video_urls)
            bot.send_video(chat_id=message.chat.id, video=selected_video, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_imganime(bot):
    @bot.message_handler(commands=['imganime'])
    def handle_imganime(message):
        try:
            file_path = "bot/url/imganime"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_photo(chat_id=message.chat.id, photo=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_butt(bot):
    @bot.message_handler(commands=['butt'])
    def handle_butt(message):
        try:
            file_path = "bot/url/butt"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_photo(chat_id=message.chat.id, photo=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_squeeze(bot):
    @bot.message_handler(commands=['squeeze'])
    def handle_squeeze(message):
        try:
            file_path = "bot/url/squeeze"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_animation(chat_id=message.chat.id, animation=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_cosplay(bot):
    @bot.message_handler(commands=['cosplay'])
    def handle_cosplay(message):
        try:
            file_path = "bot/url/cosplay"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_photo(chat_id=message.chat.id, photo=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_pussy(bot):
    @bot.message_handler(commands=['pussy'])
    def handle_pussy(message):
        try:
            file_path = "bot/url/pussy"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_photo(chat_id=message.chat.id, photo=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_nude(bot):
    @bot.message_handler(commands=['nude'])
    def handle_nude(message):
        try:
            file_path = "bot/url/nude"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_photo(chat_id=message.chat.id, photo=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")

def register_girlsexy(bot):
    @bot.message_handler(commands=['girlsexy'])
    def handle_girlsexy(message):
        try:
            file_path = "bot/url/girlsexy"
            with open(file_path, "r", encoding="utf-8") as file:
                image_urls = [line.strip() for line in file if line.strip()]
            
            if not image_urls:
                bot.reply_to(message, "Danh sách ảnh chưa có dữ liệu!")
                return

            selected_image = random.choice(image_urls)
            bot.send_photo(chat_id=message.chat.id, photo=selected_image, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")
