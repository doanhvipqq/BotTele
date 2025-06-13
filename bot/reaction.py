import random
from telebot import types

emoji_list = ['👍', '👎', '❤️', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🤮', '💩', '🙏', '👌',
              '🕊️', '🤡', '🥱', '🥴', '😍', '🐳', '❤️‍🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆', '💔', '🤨', '😐', '🍓',
              '🍾', '💋', '🖕', '😈', '😴', '😭', '🤓', '👻', '👨‍💻', '👀', '🎃', '🙈', '😇', '😨', '🤝', '✍️', '🤗', '🫡',
              '🎅', '🎄', '☃️', '💅', '🤪', '🗿', '🆒', '💘', '🙉', '🦄', '😘', '💊', '🙊', '😎', '👾', '🤷‍♂️', '🤷',
              '🤷‍♀️', '😡']

# 📌 Danh sách các nhóm được phép
allowed_chat_ids = [-1002408191237, 6379209139, 5900948782, 7944440933, 7605936504]

def register_reaction(bot):
    # 🎯 Xử lý mọi tin nhắn (mọi loại content)
    @bot.message_handler(func=lambda message: not message.text.startswith('/'), content_types=["all"])
    def handle_all_messages(message):
        chat_id = message.chat.id
        message_id = message.message_id
    
        if chat_id in allowed_chat_ids:
            emoji = random.choice(emoji_list)
            try:
                bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=message_id,
                    reaction=[types.ReactionTypeEmoji(emoji=emoji)]
                )
            except Exception:
                pass  
        else:
            try:
                bot.send_message(chat_id, "❌ Bot không thể sử dụng trong đoạn chat này!")
            except Exception:
                pass  