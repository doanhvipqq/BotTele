import requests
import html

def register_translate(bot):
    @bot.message_handler(commands=['translate', 'dich'])
    def translate(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return bot.reply_to(message, "❌ Vui lòng nhập văn bản tiếng Trung cần dịch.\nVí dụ: /translate 你好")

        text = args[1].strip()
        loading = bot.send_message(message.chat.id, f"🔄 Đang dịch: <b>{html.escape(text)}</b>")

        try:
            result = translate_chinese_to_vietnamese(text)
            if not result:
                return bot.edit_message_text("❌ Không thể dịch văn bản này.", message.chat.id, loading.message_id)

            reply = f"🇨🇳 ➡️ 🇻🇳 <b>Bản dịch:</b>\n\n<i>{html.escape(result)}</i>"

            bot.edit_message_text(
                reply,
                message.chat.id,
                loading.message_id
            )

        except Exception as e:
            bot.edit_message_text(
                f"❌ Lỗi: {html.escape(str(e))}",
                message.chat.id,
                loading.message_id
            )

def translate_chinese_to_vietnamese(text):
    """
    Dịch văn bản từ tiếng Trung sang tiếng Việt sử dụng API mduc.online
    """
    try:
        res = requests.get(
            f"https://mduc.online/api/trans/china",
            params={'text': text},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        
        if res.status_code == 200:
            data = res.json()
            # API trả về: {"input_text": "...", "status": "success", "translated_text": "..."}
            if isinstance(data, dict) and data.get('status') == 'success':
                return data.get('translated_text')
            else:
                return None
        else:
            return None
            
    except Exception as e:
        print(f"Translation error: {e}")
        return None

