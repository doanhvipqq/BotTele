import re
import time
import requests
import threading

QUEST_INFO = {
    "m88": {
        "url": "https://bet88ec.com/cach-danh-bai-sam-loc",
        "traffic": "https://bet88ec.com/",
        "codexn": "taodeptrai",
        "endpoint": "GET_MA.php",
        "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    },
    "fb88": {
        "url": "https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi",
        "traffic": "https://fb88mg.com/",
        "codexn": "taodeptrai",
        "endpoint": "GET_MA.php",
        "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    },
    "188bet": {
        "url": "https://88betag.com/cach-choi-game-bai-pok-deng",
        "traffic": "https://88betag.com/",
        "codexn": "taodeptrailamnhe",
        "endpoint": "GET_MA.php",
        "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    },
    "w88": {
        "url": "https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi",
        "traffic": "https://188.166.185.213/",
        "codexn": "taodeptrai",
        "endpoint": "GET_MA.php",
        "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    },
    # "v9bet": {
    #     "url": "https://v9betho.com/ca-cuoc-bong-ro-ao",
    #     "traffic": "https://v9betho.com/",
    #     "codexn": "taodeptrai",
    #     "endpoint": "GET_MA.php",
    #     "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    # },
    # "vn88": {
    #     "url": "https://vn88no.com/keo-chap-1-trai-la-gi",
    #     "traffic": "https://vn88no.com/",
    #     "codexn": "bomaydeptrai",
    #     "endpoint": "GET_MA.php",
    #     "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    # },
    # "bk8": {
    #     "url": "https://bk8ze.com/cach-choi-bai-catte",
    #     "traffic": "https://bk8ze.com/",
    #     "codexn": "taodeptrai",
    #     "endpoint": "GET_MA.php",
    #     "regex": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
    # },
    "88betag": {
        "url": "https://88betag.com/keo-chau-a-la-gi",
        "traffic": "https://88betag.com/",
        "codexn": "bomaylavua",
        "endpoint": "GET_MD.php",
        "regex": r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>'
    }
}

def process_yeumoney_step(bot, message, sent_msg, code):
    for remaining in range(75, 0, -5):
        try:
            bot.edit_message_text(
                f"⏳ Đang xử lý... vui lòng chờ {remaining} giây.",
                message.chat.id,
                sent_msg.message_id
            )
        except:
            pass
        time.sleep(5)

    bot.edit_message_text(
        f"» <b>Mã của bạn là:</b> <blockquote>{code}</blockquote>\n🎉 Hãy nhập mã để lấy link đích.",
        message.chat.id,
        sent_msg.message_id,
    )

def register_yeumoney(bot):
    @bot.message_handler(commands=['ymn'])
    def handle_get_code(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "🚫 Vui lòng nhập từ khoá.\nVí dụ: /ymn m88")
            return

        key = args[1].strip().lower()
        info = QUEST_INFO.get(key)

        if not info:
            bot.reply_to(message, "🚫 Từ khoá không hỗ trợ.\nHỗ trợ: " + ', '.join(QUEST_INFO.keys()))
            return

        try:
            # Phân biệt key codexn/codexnd theo endpoint
            param_key = "codexn" if info["endpoint"] == "GET_MA.php" else "codexnd"

            response = requests.post(
                f"https://traffic-user.net/{info['endpoint']}",
                params={
                    param_key: info["codexn"],
                    "url": info["url"],
                    "loai_traffic": info["traffic"],
                    "clk": 1000
                },
                timeout=15
            )

            html = response.text
            match = re.search(info["regex"], html)

            if match:
                code = match.group(1)
                sent_msg = bot.send_message(
                    message.chat.id,
                    "⏳ Đang xử lý... Vui lòng chờ!",
                    reply_to_message_id=message.message_id
                )
                threading.Thread(
                    target=process_yeumoney_step,
                    args=(bot, message, sent_msg, code),
                    daemon=True
                ).start()
            else:
                bot.reply_to(message, "⚠️ Không tìm thấy mã.")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Lỗi: {e}")
