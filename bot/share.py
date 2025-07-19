import requests
import threading
import time

DELAY = 10  # giây

gome_token = []

def get_token_from_cookies(file_path='cookies.txt'):
    tokens = []
    try:
        with open(file_path, 'r') as f:
            cookies = f.read().splitlines()
        for cookie in cookies:
            headers = {
                'cookie': cookie,
                'referer': 'https://www.facebook.com/',
            }
            try:
                res = requests.get('https://business.facebook.com/content_management', headers=headers).text
                token = res.split('EAAG')[1].split('","')[0]
                tokens.append(f'{cookie}|EAAG{token}')
            except:
                pass
    except FileNotFoundError:
        pass
    return tokens

def share_action(token_data, id_share, bot, chat_id, index):
    cookie, token = token_data.split('|')
    headers = {
        'cookie': cookie,
        'host': 'graph.facebook.com'
    }
    try:
        requests.post(
            f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_share}&published=0&access_token={token}',
            headers=headers
        )
        bot.send_message(chat_id, f"✅ Share #{index + 1} thành công: {id_share}")
    except:
        bot.send_message(chat_id, f"❌ Share #{index + 1} thất bại.")

def register_share(bot):
    @bot.message_handler(commands=['share'])
    def handle_share(message):
        try:
            args = message.text.split()
            if len(args) != 3:
                bot.reply_to(message, "❗ Sử dụng đúng cú pháp: /share <ID> <Số lượng>\nID có thể lấy từ: https://id.traodoisub.com/")
                return

            id_share = args[1]
            total_share = int(args[2])
            tokens = get_token_from_cookies()

            if not tokens:
                bot.reply_to(message, "⚠️ Không có cookie hợp lệ trong file `cookies.txt`.")
                return

            bot.send_message(message.chat.id, f"🚀 Bắt đầu share ID: {id_share}\n🕓 Delay: {DELAY}s\n📦 Tổng số share: {total_share}")
            
            for i in range(total_share):
                token = tokens[i % len(tokens)]
                threading.Thread(target=share_action, args=(token, id_share, bot, message.chat.id, i)).start()
                time.sleep(DELAY)

        except Exception as e:
            bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

