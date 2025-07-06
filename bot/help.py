caption = """<blockquote expandable>┌───────────────⭓
├ /help: Menu bot
├ /admin: Info admin
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
├───────────────⭔
├ /pussy: 🔞
├ /r34: Ảnh r34 🔞
├ /squeeze: Bóp 🌚
├ /girl: Video gái 😳
├ /butt: Ảnh mông gái 🙅‍♀️
├ /anime: Video anime 🇯🇵
├ /imganime: Ảnh anime 🦄
├ /cosplay: Ảnh cosplay 🧝‍♀️
├ /nude: Ảnh bán thoả thân 🔞
└───────────────⭓
</blockquote>"""

def register_help(bot):
    @bot.message_handler(commands=['help', 'start'])
    def send_help(message):
        bot.reply_to(message, caption)
