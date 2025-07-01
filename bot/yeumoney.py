import re
import requests

# Danh sách các loại quest và thông tin tương ứng
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
    }
}


def register_yeumoney(bot):
    @bot.message_handler(commands=['ymn'])
    def handle_get_code(message):
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            bot.reply_to(
                message,
                "🚫 Vui lòng nhập từ khoá muốn lấy mã.\nVí dụ: /ymn m88"
            )
            return

        quest_type = args[1].strip().lower()
        info = QUEST_INFO.get(quest_type)

        if not info:
            bot.reply_to(message, "🚫 Loại quest không hợp lệ.")
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
                bot.reply_to(
                    message,
                    f"» Mã: <blockquote>{code}</blockquote>\nVui lòng đợi 75s mới nhập mã để tránh lỗi",
                    parse_mode='HTML'
                )
            else:
                bot.reply_to(message, "⚠️ Không tìm thấy mã.")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Lỗi: {e}")
