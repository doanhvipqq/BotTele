# main_bot.py
import os
import telebot
from bot.nct import register_nct
from bot.scl import register_scl
from bot.girl import register_girl
from bot.images import register_images

# Lấy token từ biến môi trường
TOKEN = "os.getenv("TELEGRAM_TOKEN")"
bot = telebot.TeleBot(TOKEN)

# Đăng ký các handler từ các file module khác nhau
register_nct(bot)
register_scl(bot)
register_girl(bot)
register_images(bot)

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
