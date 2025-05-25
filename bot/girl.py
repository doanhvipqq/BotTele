import random
import telebot

def register_girl(bot: telebot.TeleBot):
    @bot.message_handler(commands=['girl'])
    def send_girl_video(message):
        try:
            file_path = "bot/url/girl.txt"
            with open(file_path, "r", encoding="utf-8") as file:
                video_urls = [line.strip() for line in file if line.strip()]
            
            if not video_urls:
                bot.reply_to(message, "Danh sách video chưa có dữ liệu!")
                return

            selected_video = random.choice(video_urls)
            bot.send_video(chat_id=message.chat.id, video=selected_video)
        except Exception as e:
            print("Lỗi:", e)  # In ra lỗi chi tiết để bạn debug
            bot.reply_to(message, "Đã xảy ra lỗi khi xử lý video.")