caption = """ ‎‧₊˚✧ <b>Bóng X Bot</b> ✧˚₊‧

<blockquote expandable><b>📋 TIỆN ÍCH CƠ BẢN</b>
├ /help - Menu bot
├ /start - Khởi động bot
├ /time - Xem giờ hiện tại
├ /encode - Mã hóa/giải mã
├ /share - Chia sẻ file
├ /send - Gửi tin nhắn
└ /in4 - Thông tin user/group</blockquote>

<blockquote expandable><b>🎵 TẢI MEDIA</b>
├ /tiktok - Tải video TikTok
├ /scl - Tải nhạc SoundCloud
├ /nct - Tải nhạc NhạcCủaTui
├ /search - Tìm kiếm Google
└ /meme - Random meme</blockquote>

<blockquote expandable><b>🛠️ TOOLS</b>
├ /proxy - Lấy proxy
├ /github - Thông tin GitHub
├ /sourceweb - Lấy source code website
├ /link4sub - Link4Sub tools
├ /reg - Random acc liên quân
├ /thumb - Thêm thumbnail cho file
└ /images - Lấy URL ảnh từ web</blockquote>

<blockquote expandable><b>📲 SMS TOOLS</b>
├ /spamsms - SMS spam
├ /smsvip - SMS VIP (Chỉ VIP)
└ /add - Thêm VIP (Admin)</blockquote>

<blockquote expandable><b>🎬 RANDOM MEDIA</b>
├ /anime - Random video anime
├ /girl - Random video girl
└ /imganime - Random ảnh anime</blockquote>

<blockquote expandable><b>👮 QUẢN LÝ NHÓM (ADMIN)</b>
├ /kick - Kick và ban vĩnh viễn
├ /ban - Cấm chat có thời hạn
└ /unban - Bỏ cấm</blockquote>

<i>💡 Gõ / để xem gợi ý lệnh!</i>
"""

def register_help(bot):
    @bot.message_handler(commands=['help', 'start'])
    def send_help(message):
        bot.reply_to(message, caption)
