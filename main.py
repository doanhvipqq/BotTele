import os
import telebot
import threading
from flask import Flask
from dotenv import load_dotenv

# --- CẤU HÌNH WEB SERVER GIẢ ĐỂ RENDER KHÔNG TẮT BOT ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang chạy ổn định!"

def run_web_server():
    # Render sẽ cung cấp cổng qua biến môi trường PORT, nếu không có thì dùng 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web_server)
    t.start()
# -------------------------------------------------------

load_dotenv()

# --- TOKEN ---
TOKEN = "8567340377:AAG9LLjKin8NjJDtIWDsS7jXa_vogHY6nMI"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
# -------------

# --- CÁC MODULE GIỮ LẠI (TIỆN ÍCH, SYSTEM) ---

from bot.encode import register_encode
register_encode(bot)

from bot.share import register_share
register_share(bot)

from bot.scl import register_scl
register_scl(bot)

from bot.in4 import register_in4
register_in4(bot)

from bot.send import register_send
register_send(bot)

from bot.time import register_time
register_time(bot)

from bot.help import register_help
register_help(bot)

from bot.proxy import register_proxy
register_proxy(bot)

from bot.random import register_random
register_random(bot)

from bot.tiktok import register_tiktok
register_tiktok(bot)

from bot.github import register_github
register_github(bot)

from bot.search import register_search
register_search(bot)

from bot.meme import register_meme
register_meme(bot)

from bot.spamsms import register_spamsms
register_spamsms(bot)

from bot.sourceweb import register_sourceweb
register_sourceweb(bot)


# --- CÁC MODULE ĐÃ BỊ TẮT (THEO YÊU CẦU CỦA BẠN) ---
# Đã thêm dấu # ở đầu dòng để vô hiệu hóa lệnh

# Reaction (Chứa /squeeze)
from bot.bypass import register_bypass
register_bypass(bot)

# Ảnh Cosplay (/cosplay)
# from bot.cosplay import register_bot/share
# register_share(bot)

# Ảnh R34 (/r34)
# from bot.r34 import register_r34
# register_r34(bot)

# Ảnh 18+, Pixxx (/pussy, /nude, /butt...)
# from bot.pixxx import register_pixxx
# register_pixxx(bot)

# Ảnh Anime, Nekos (/anime, /imganime)
# from bot.nekos import register_nekos
# register_nekos(bot)

# Các module ảnh khác
# from bot.img import register_img
# register_img(bot)

# from bot.img1 import register_img1
# register_img1(bot)

# from bot.images import register_images
# register_images(bot)

# from bot.thumb import register_thumb
# register_thumb(bot)

# Nội dung người lớn/Lầu xanh (/lx, /lxmanga)
# from bot.lx import register_lx
# register_lx(bot)

# from bot.lxmanga import register_lxmanga
# register_lxmanga(bot)

# from bot.nct import register_nct
# register_nct(bot)

# from bot.funlink import register_funlink
# register_funlink(bot)

# from bot.yeumoney import register_yeumoney
# register_yeumoney(bot)


if __name__ == '__main__':
    # Chạy Web Server giả trên luồng riêng
    keep_alive()
    
    print("Bot đang chạy (Đã tắt các lệnh NSFW/Anime)...")
    bot.infinity_polling()
