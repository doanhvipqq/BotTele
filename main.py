from telegram.ext import Updater
from config import BOT_TOKEN

# Import handler từ các module con
from handlers.girl_handler import get_handler as girl_handler
from handlers.images_handler import get_handler as images_handler
from handlers.sourceweb_handler import get_handler as sourceweb_handler
from handlers.tiktok_handler import get_handler as tiktok_handler
from handlers.anime_handler import get_handler as anime_handler
from handlers.emoji_handler import get_handler as emoji_handler
from handlers.scl_beta_handler import get_handler as scl_beta_handler

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Thêm các handler vào dispatcher
    dp.add_handler(girl_handler())
    dp.add_handler(images_handler())
    dp.add_handler(sourceweb_handler())
    dp.add_handler(tiktok_handler())
    dp.add_handler(anime_handler())
    dp.add_handler(emoji_handler())
    dp.add_handler(scl_beta_handler())

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
