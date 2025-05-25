# main_bot.py
import os
import telebot
from bot.girl import register_girl
from bot.images import register_images
from bot.scl import register_scl

# Lấy token từ biến môi trường
TOKEN = "7757320016:AAEyc-YORyiR2aPz4UTrz7LHNHveSq9NgZw"
bot = telebot.TeleBot(TOKEN)

# Đăng ký các handler từ các file module khác nhau
register_girl(bot)
register_images(bot)
register_scl(bot)

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
