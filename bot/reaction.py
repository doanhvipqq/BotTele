import random
from telebot import types
from config import GROUP_ID

emoji_list = ['👍', '👎', '❤️', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🤮', '💩', '🙏', '👌',
              '🕊️', '🤡', '🥱', '🥴', '😍', '🐳', '❤️‍🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆', '💔', '🤨', '😐', '🍓',
              '🍾', '💋', '🖕', '😈', '😴', '😭', '🤓', '👻', '👨‍💻', '👀', '🎃', '🙈', '😇', '😨', '🤝', '✍️', '🤗', '🫡',
              '🎅', '🎄', '☃️', '💅', '🤪', '🗿', '🆒', '💘', '🙉', '🦄', '😘', '💊', '🙊', '😎', '👾', '🤷‍♂️', '🤷', '🤷‍♀️', '😡']

def register_reaction(bot):
    content_types = ['text', 'photo', 'video', 'sticker', 'audio', 'document', 'voice']

    def create_handler(content_type):
        @bot.message_handler(content_types=[content_type])
        def handle_message(message):
            # Nếu chỉ muốn phản ứng trong group nhất định:
            # if message.chat.id not in GROUP_ID:
            #     return
            emoji = random.choice(emoji_list)
            try:
                bot.set_message_reaction(
                    message.chat.id,
                    message.message_id,
                    reaction=[types.ReactionTypeEmoji(emoji)]
                )
            except Exception:
                pass

    for ct in content_types:
        create_handler(ct)