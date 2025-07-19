import requests
import threading
import time

COOKIES = [
    "c_user=61576745407310;xs=1:mX-BpIZeF-XFQQ:2:1748624475:-1:-1;dpr=0.22140221297740936;locale=vi_VN;wl_cbv=v2%3Bclient_version%3A2839%3Btimestamp%3A1749362040;datr=U-Q5aE6ju_MeWbcBeo3UjUP-;sb=ZyVFaPAAk7gvctAyTkZ24CxU;ps_n=1;ps_l=1;fbl_st=101535528%3BT%3A29156034;wd=1600x753;fr=0pQfUAOZBw55GpckG.AWfn1-Sn6gYiLR2DINiQCRC_3hWytJzlJZlLgGFh15WTkYw15z4.BoRSVc..AAA.0.0.Boex_J.AWdDQr1dvJK0DGMseRqs897LHhQ;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752900131582%2C%22v%22%3A1%7D;",
    "c_user=61576745407310;xs=1:mX-BpIZeF-XFQQ:2:1748624475:-1:-1;dpr=0.22140221297740936;locale=vi_VN;wl_cbv=v2%3Bclient_version%3A2839%3Btimestamp%3A1749362040;datr=U-Q5aE6ju_MeWbcBeo3UjUP-;sb=ZyVFaPAAk7gvctAyTkZ24CxU;ps_n=1;ps_l=1;fbl_st=101535528%3BT%3A29156034;wd=1600x753;fr=0pQfUAOZBw55GpckG.AWfn1-Sn6gYiLR2DINiQCRC_3hWytJzlJZlLgGFh15WTkYw15z4.BoRSVc..AAA.0.0.Boex_J.AWdDQr1dvJK0DGMseRqs897LHhQ;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752900131582%2C%22v%22%3A1%7D;",
    # "cookie3",  # Bỏ comment để thêm cookie
]

def get_token(cookies):
    tokens = []
    for cookie in cookies:
        headers = {
            'cookie': cookie,
            'referer': 'https://www.facebook.com/',
            'user-agent': 'Mozilla/5.0'
        }
        try:
            res = requests.get('https://business.facebook.com/content_management', headers=headers).text
            token = res.split('EAAG')[1].split('","')[0]
            tokens.append(f'{cookie}|EAAG{token}')
        except:
            pass
    return tokens

def share(cookie_token, id_share):
    cookie, token = cookie_token.split('|')
    headers = {
        'cookie': cookie,
        'host': 'graph.facebook.com'
    }
    try:
        requests.post(
            f'https://graph.facebook.com/me/feed?link=https://m.facebook.com/{id_share}&published=0&access_token={token}',
            headers=headers
        )
    except:
        pass

def register_share(bot):
    @bot.message_handler(commands=['share'])
    def handle_share(message):
        args = message.text.split()[1:]
        if len(args) != 2:
            bot.reply_to(message, "❗ Dùng đúng cú pháp: /share <id> <số lượng>")
            return

        id_share = args[0]
        try:
            total = int(args[1])
        except:
            bot.reply_to(message, "❗ Số lượng phải là số nguyên.")
            return

        accounts = get_token(COOKIES)
        if not accounts:
            bot.reply_to(message, "⚠️ Không có cookie hợp lệ.")
            return

        status = bot.reply_to(message, f"🚀 Bắt đầu share ID: {id_share} [0/{total}]")
        count = 0

        while count < total:
            for acc in accounts:
                if count >= total:
                    break
                threading.Thread(target=share, args=(acc, id_share)).start()
                count += 1
                try:
                    bot.edit_message_text(f"[{count}/{total}] Đã share ID: {id_share}", status.chat.id, status.message_id)
                except:
                    pass
                time.sleep(10)

        bot.edit_message_text(f"✅ Hoàn tất share! [{count}/{total}]", status.chat.id, status.message_id)
