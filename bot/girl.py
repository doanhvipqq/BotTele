import telebot
import random

def register_girl(bot: telebot.TeleBot):
    @bot.message_handler(commands=['girl'])
    def send_girl_video(message):
        """
        Xử lý lệnh /girl:
          - Đọc file video từ đường dẫn cố định: url/girl.txt.
          - Chọn ngẫu nhiên một URL video chứa trong file.
          - Gửi video đến người dùng.
        """
        try:
            # Sử dụng đường dẫn cố định "url/girl.txt"
            with open("url/girl.txt", "r", encoding="utf-8") as file:
                video_urls = [line.strip() for line in file if line.strip()]

            if not video_urls:
                bot.reply_to(message, "Danh sách video chưa có dữ liệu!")
                return

            # Chọn ngẫu nhiên một URL video
            selected_video = random.choice(video_urls)
            bot.send_video(chat_id=message.chat.id, video=selected_video)
        except Exception as e:
            print("Lỗi:", e)
            bot.reply_to(message, "Đã xảy ra lỗi khi xử lý video.")