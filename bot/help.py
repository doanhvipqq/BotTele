caption = """ ‎‧₊˚✧ <b>Bóng X Bot</b> ✧˚₊‧

<blockquote expandable>📋 <b>DANH SÁCH LỆNH</b>
├ /help - Menu bot
├ /start - Khởi động bot
├ /time - Xem giờ hiện tại
├ /encode - Mã hóa/giải mã
├ /share - Chia sẻ file
├ /send - Gửi tin nhắn
├ /in4 - Thông tin user/group
├ /tiktok - Tải video TikTok
├ /scl - Tải nhạc SoundCloud
├ /nct - Tải nhạc NhạcCủaTui
├ /search - Tìm kiếm Google
├ /translate - Dịch Trung-Việt 🇨🇳➡️🇻🇳
├ /meme - Random meme
├ /proxy - Lấy proxy
├ /github - Thông tin GitHub
├ /sourceweb - Lấy source code website
├ /link4sub - Link4Sub tools
├ /reg - Random acc liên quân
├ /thumb - Thêm thumbnail cho file
├ /images - Lấy URL ảnh từ web
├ /spamsms - SMS spam
├ /smsvip - SMS VIP (Chỉ VIP)
├ /add - Thêm VIP (Admin)
├ /anime - Random video anime
├ /girl - Random video girl
├ /imganime - Random ảnh anime
├ /kick - Kick và ban vĩnh viễn (Admin)
├ /ban - Cấm chat có thời hạn (Admin)
└ /unban - Bỏ cấm (Admin)</blockquote>

<i>💡 Gõ / để xem gợi ý lệnh!</i>
"""

def register_help(bot):
    @bot.message_handler(commands=['help', 'start'])
    def send_help(message):
        bot.reply_to(message, caption)

