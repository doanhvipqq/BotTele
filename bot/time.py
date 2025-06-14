import time
import random
from datetime import timedelta

start_time = time.time()
file_path = "bot/url/anime"

def get_uptime():
    return str(timedelta(seconds=int(time.time() - start_time)))

def anime_video():
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            video_urls = [line.strip() for line in file if line.strip()]
        
        if not video_urls:
            return None

        return random.choice(video_urls)
    except Exception as e:
        return None

def register_time(bot):
    @bot.message_handler(commands=['time'])
    def send_time(message):
        uptime = get_uptime()
        video_url = anime_video()

        if not video_url:
            bot.reply_to(message, "Không thể lấy video anime.")
            return
        
        caption = f"<blockquote><b>⏳ Thời gian mà Bot đã hoạt động là:</b> {uptime}</blockquote>"
        bot.send_video(
            message.chat.id,
            video_url,
            caption = caption
        )
