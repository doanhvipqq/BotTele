# main_bot.py
import os
import telebot
from bot.nct import register_nct
from bot.scl import register_scl
from bot.time import register_time
from bot.help import register_help
from bot.random import *
from bot.images import register_images
from bot.github import register_github
from bot.thongtin import register_thongtin

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Đăng ký các handler từ các file module khác nhau
register_nct(bot)
register_scl(bot)
register_time(bot)
register_help(bot)
register_thongtin(bot)

# Random
register_girl(bot)
register_anime(bot)
register_imganime(bot)
register_butt(bot)
register_squeeze(bot)
register_cosplay(bot)
register_pussy(bot)
register_nude(bot)
register_girlsexy(bot)
#############################
register_images(bot)
register_github(bot)

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
