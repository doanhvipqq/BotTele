import re
import time
import requests

QUEST_INFO = {
    "m88": {
        "url": "https://bet88ec.com/cach-danh-bai-sam-loc",
        "traffic": "https://bet88ec.com/",
        "codexn": "taodeptrai"
    },
    "fb88": {
        "url": "https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi",
        "traffic": "https://fb88mg.com/",
        "codexn": "taodeptrai"
    },
    "188bet": {
        "url": "https://88betag.com/cach-choi-game-bai-pok-deng",
        "traffic": "https://88betag.com/",
        "codexn": "taodeptrailamnhe"
    },
    "w88": {
        "url": "https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi",
        "traffic": "https://188.166.185.213/",
        "codexn": "taodeptrai"
    },
    "v9bet": {
        "url": "https://v9betse.com/ca-cuoc-dua-cho",
        "traffic": "https://v9betse.com/",
        "codexn": "taodeptrai"
    }
}

def register_yeumoney(bot):
    @bot.message_handler(commands=['ymn'])
    def handle_get_code(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng nhập từ khoá muốn lấy mã.\nVí dụ: /ymn m88")
            return

        key = args[1].strip().lower()
        info = QUEST_INFO.get(key)

        if not info:
            bot.reply_to(message, "🚫 Từ khoá này hiện chưa được hỗ trợ.\nCác từ khoá đang hỗ trợ gồm: m88, fb88, 188bet, w88, v9bet")
            return

        try:
            response = requests.post(
                "https://traffic-user.net/GET_MA.php",
                params={
                    "codexn": info["codexn"],
                    "url": info["url"],
                    "loai_traffic": info["traffic"],
                    "clk": 1000
                }
            )
            html = response.text
            match = re.search(
                r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                html
            )

            if match:
                code = match.group(1)
                sent_msg = bot.send_message(
                    message.chat.id,
                    f"⏳ Đang xử lý...",
                    reply_to_message_id=message.message_id
                )

                for remaining in range(75, 0, -5):
                    bot.edit_message_text(
                        f"⏳ Đang xử lý... vui lòng chờ {remaining} giây.",
                        message.chat.id,
                        sent_msg.message_id,
                    )
                    time.sleep(5)

                # Kết thúc đếm ngược
                bot.edit_message_text(
                    f" » <b>Mã của bạn là:</b> <blockquote>{code}</blockquote>\n🎉 Hãy nhập mã để lấy link đích.",
                    message.chat.id,
                    sent_msg.message_id,
                )

            else:
                bot.reply_to(message, "⚠️ Không tìm thấy mã.")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Lỗi: {e}")