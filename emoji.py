import os
import json
import random
import requests
import telebot

# Lấy token từ biến môi trường
bot_token = os.getenv("TELEGRAM_TOKEN")

# Danh sách emoji để thả (reaction)
emoji_list = [
    '👍', '👎', '❤️', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢',
    '🎉', '🤩', '🤮', '💩', '🙏', '👌', '🕊️', '🤡', '🥱', '🥴', '😍', '🐳',
    '❤️‍🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆', '💔', '🤨', '😐', '🍓',
    '🍾', '💋', '🖕', '😈', '😴', '😭', '🤓', '👻', '👨‍💻', '👀', '🎃', '🙈',
    '😇', '😨', '🤝', '✍️', '🤗', '🫡', '🎅', '🎄', '☃️', '💅', '🤪', '🗿',
    '🆒', '💘', '🙉', '🦄', '😘', '💊', '🙊', '😎', '👾', '🤷‍♂️', '🤷',
    '🤷‍♀️', '😡'
]

# Danh sách ID các nhóm được phép
allowed_chat_ids = [-1002408191237, 6379209139, 5900948782, 7944440933, 7605936504]

def thaCamXuc(chat_id, message_id, emoji):
    """
    Gọi API setMessageReaction để thả emoji vào tin nhắn.
    """
    url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': json.dumps([{'type': 'emoji', 'emoji': emoji}])
    }
    response = requests.post(url, data=data)
    return response.json()

def register_reaction_handlers(bot):
    """
    Đăng ký các handler để tự động thả reaction (emoji) cho tin nhắn.
    
    Các tin nhắn từ các chat cho phép (allowed_chat_ids) sẽ được bot chọn ngẫu nhiên emoji 
    và gọi API setMessageReaction.
    Nếu tin nhắn đến từ chat không được phép, bot sẽ gửi thông báo cảnh báo.
    """
    # Handler cho các tin nhắn đến từ các nhóm cho phép
    @bot.message_handler(func=lambda m: m.chat.id in allowed_chat_ids)
    def allowed_reaction_handler(message):
        random_emoji = random.choice(emoji_list)
        result = thaCamXuc(message.chat.id, message.message_id, random_emoji)
        print(f"Đã thả {random_emoji} vào tin nhắn {message.message_id} trong nhóm {message.chat.id}")
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    # Handler cho các tin nhắn đến từ các chat không được phép
    @bot.message_handler(func=lambda m: m.chat.id not in allowed_chat_ids)
    def disallowed_handler(message):
        bot.send_message(message.chat.id, "Bot không thể sử dụng trong đoạn chat này!")
