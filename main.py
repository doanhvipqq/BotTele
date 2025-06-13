# main_bot.py
import os
import telebot
from bot.nct import register_nct
from bot.scl import register_scl
from bot.time import register_time
from bot.help import register_help
from bot.random import register_random
from bot.tiktok import register_tiktok
from bot.images import register_images
from bot.github import register_github
from bot.search import register_search
from bot.spamsms import register_spamsms
from bot.lxmanga import register_lxmanga
from bot.reaction import register_reaction
from bot.thongtin import register_thongtin
from bot.sourceweb import register_sourceweb

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

register_nct(bot)
register_scl(bot)
register_time(bot)
register_help(bot)
register_images(bot)
register_github(bot)
register_random(bot)
register_tiktok(bot)
register_search(bot)
register_spamsms(bot)
register_lxmanga(bot)
register_thongtin(bot)
register_sourceweb(bot)
###########
register_reaction(bot) # Luôn luôn đặt ở cuối

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()