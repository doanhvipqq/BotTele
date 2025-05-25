import random

def register_girl(bot):
    @bot.message_handler(commands=['girl'])
    def handle_girl(message):
        try:
            file_path = "bot/url/girl.txt"
            with open(file_path, "r", encoding="utf-8") as file:
                video_urls = [line.strip() for line in file if line.strip()]
            
            if not video_urls:
                bot.reply_to(message, "Danh sách video chưa có dữ liệu!")
                return

            selected_video = random.choice(video_urls)
            bot.send_video(chat_id=message.chat.id, video=selected_video, reply_to_message_id=message.message_id)
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {e}")