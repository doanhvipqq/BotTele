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
TOKEN = "8567340377:AAEJwIDvHNKAw0cs8Mr_DiQMoVIORJRZSqA"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# --- THIẾT LẬP GỢI Ý LỆNH (BOTCOMMAND) ---
from telebot.types import BotCommand

commands = [
    BotCommand("help", "📋 Xem danh sách lệnh"),
    BotCommand("time", "🕐 Xem giờ hiện tại"),
    BotCommand("encode", "🔐 Mã hóa/giải mã"),
    BotCommand("share", "📤 Chia sẻ file"),
    BotCommand("send", "💬 Gửi tin nhắn"),
    BotCommand("in4", "ℹ️ Thông tin user/group"),
    BotCommand("tiktok", "📱 Tải video TikTok"),
    BotCommand("scl", "🎧 Tải SoundCloud"),
    BotCommand("search", "🔍 Tìm kiếm Google"),
    BotCommand("meme", "😂 Random meme"),
    BotCommand("proxy", "🌐 Lấy proxy"),
    BotCommand("github", "💻 Thông tin GitHub"),
    BotCommand("spamsms", "📲 SMS tools"),
    BotCommand("add", "➕ Thêm VIP (Admin)"),
    BotCommand("smsvip", "💎 SMS VIP (Chỉ VIP)"),
    BotCommand("sourceweb", "🌍 Lấy source code website"),
    BotCommand("link4sub", "🔗 Link4Sub tools"),
    BotCommand("reg", "📝 Đăng ký tools"),
    BotCommand("nct", "🎵 Tải nhạc NhạcCủaTui"),
    BotCommand("thumb", "🖼️ Thêm thumbnail cho file"),
    BotCommand("images", "📷 Lấy URL ảnh từ web"),
    BotCommand("anime", "🎬 Random video anime"),
    BotCommand("girl", "👧 Random video girl"),
    BotCommand("imganime", "🖼️ Random ảnh anime"),
    # Lệnh admin (chỉ admin mới dùng được)
    BotCommand("kick", "🚫 Kick và ban vĩnh viễn (Admin)"),
    BotCommand("ban", "🔇 Cấm chat có thời hạn (Admin)"),
    BotCommand("unban", "✅ Bỏ cấm (Admin)"),
]

bot.set_my_commands(commands)
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

from bot.nct import register_nct
register_nct(bot)

from bot.thumb import register_thumb
register_thumb(bot)

from bot.images import register_images
register_images(bot)

from bot.reaction import register_reaction
register_reaction(bot)

from bot.admin import register_admin
register_admin(bot)



# --- CÁC MODULE ĐÃ BỊ TẮT (THEO YÊU CẦU CỦA BẠN) ---
# Đã thêm dấu # ở đầu dòng để vô hiệu hóa lệnh

# Reaction (Chứa /squeeze)

# Ảnh Cosplay (/cosplay)
# Sửa từ: from bot.reg import register_bot/reg
# Thành:
from bot.reg import register_handlers
register_handlers(bot)
# Ảnh R34 (/r34)
# from bot.r34 import register_r34
# register_r34(bot)

# --- Thêm vào main.py ---
# Sửa trong main.py
from bot.link4sub import register_link4sub  # Import file link4sub
register_link4sub(bot)                      # Truyền bot vào đúng tên
# Ảnh Anime, Nekos (/anime, /imganime)
# from bot.nekos import register_nekos
# register_nekos(bot)

# Các module ảnh khác
# from bot.img import register_img (ĐÃ XÓA - NSFW)
# register_img(bot)

#from bot.link4m import register_link4m
#register_link4m(bot)

# Module images đã được thêm vào phía trên (dòng ~89)

# Module thumb đã được thêm vào phía trên (dòng ~93)

# Nội dung người lớn/Lầu xanh (/lx, /lxmanga)
# from bot.lx import register_lx
# register_lx(bot)

# from bot.lxmanga import register_lxmanga
# register_lxmanga(bot)

# Module nct đã được thêm vào phía trên (dòng ~81)

# from bot.funlink import register_funlink
# register_funlink(bot)

# from bot.yeumoney import register_yeumoney
# register_yeumoney(bot)


if __name__ == '__main__':
    # Chạy Web Server giả trên luồng riêng
    keep_alive()
    
    print("Bot đang chạy (Đã tắt các lệnh NSFW/Anime)...")
    bot.infinity_polling()
