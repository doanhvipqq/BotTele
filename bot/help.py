caption = """ ‎‧₊˚✧ <b>Bóng x</b> ✧˚₊‧
<blockquote expandable>┌───────────────⭓
├ /help: Menu bot
├ /time: Check time bot
├───────────────⭔
├ /proxy: Proxy free 📦
├ /github: Info github 🐈‍⬛
├ /images: Lấy url ảnh web 👻
├ /scl: Tải nhạc SoundCloud 🎶
├ /thumb: Thêm thumnail file 🌃
├ /sourceweb: Tải source web 🎃
├ /send: Tải video đa nền tảng 🎬
├ /tiktok: Thông tin video TikTok 🫦
├ /in4: Thông tin người dùng Tele 👾
‎└───────────────⭓</blockquote>

 ‎‧₊˚✧ <b>Bóng X</b> ✧˚₊‧
<blockquote expandable>✧═════• ༺༻ •═════✧
   • /meme: Meme 😂
   • /girl: Video gái 👍
   • /anime: Video anime 🇯🇵
   • /sms:spam: số điện thoại lỏ 😭
   • /smsvip: lỏ ai muốn thì ib free 
   • /reg : tạo acc ramdom
✧═════• ༺༻ •═════✧
</blockquote>"""

def register_help(bot):
    @bot.message_handler(commands=['help', 'start'])
    def send_help(message):
        bot.reply_to(message, caption)
