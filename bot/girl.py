import requests

def register_girl(bot):
    @bot.message_handler(commands=['girl'])
    def handle_girl(message):
        try:
            # Lấy video URL từ API
            api_url = "https://api-girl.onrender.com/api/girl"
            response = requests.get(api_url, timeout=10).json()
            video_url = response['video_url']
            
            try:
                # Gửi video lên Telegram
                bot.send_video(
                    chat_id=message.chat.id,
                    video=video_url,
                    reply_to_message_id=message.message_id,
                    timeout=20
                )
            except Exception as e:
                # Xử lý lỗi khi gửi video (ví dụ: URL lỗi)
                bot.reply_to(message, f"Link lỗi: {video_url}")
        except Exception as e:
            # Xử lý lỗi khi gọi API
            bot.reply_to(message, "Lỗi API!")
