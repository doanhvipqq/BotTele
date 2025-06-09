caption = """<pre>┌───────────────⭓
├ /help: Menu bot
├ /admin: Info admin
├ /time: Check time bot
├ /tiktok: Lấy thông tin video TikTok
├ /thongtin: Lấy thông tin người dùng
├───────────────⭔
├ /github: Info github 🐈‍⬛
├ /images: Lấy url ảnh web 👻
├ /scl: Tải nhạc SoundCloud 🎶
├ /sourceweb: Tải source web 🎃
├───────────────⭔
├ /pussy: 🔞
├ /squeeze: Bóp 🌚
├ /girl: Video gái 😳
├ /butt: Ảnh mông gái 🙅‍♀️
├ /anime: Video anime 🇯🇵
├ /imganime: Ảnh anime 🦄
├ /cosplay: Ảnh cosplay 🧝‍♀️
├ /nude: Ảnh bán thoả thân 🔞
└───────────────⭓
</pre>"""

def register_help(bot):
    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.reply_to(message, caption, parse_mode='HTML')