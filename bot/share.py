import requests
import threading
import time

# Thay bằng token bot Telegram của bạn

# Danh sách cookies, nhập trực tiếp ở đây
COOKIES = [
    "c_user=61576745407310;xs=1:mX-BpIZeF-XFQQ:2:1748624475:-1:-1;dpr=0.22140221297740936;locale=vi_VN;wl_cbv=v2%3Bclient_version%3A2839%3Btimestamp%3A1749362040;datr=U-Q5aE6ju_MeWbcBeo3UjUP-;sb=ZyVFaPAAk7gvctAyTkZ24CxU;ps_n=1;ps_l=1;fbl_st=101535528%3BT%3A29156034;wd=1600x753;fr=0pQfUAOZBw55GpckG.AWfn1-Sn6gYiLR2DINiQCRC_3hWytJzlJZlLgGFh15WTkYw15z4.BoRSVc..AAA.0.0.Boex_J.AWdDQr1dvJK0DGMseRqs897LHhQ;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752900131582%2C%22v%22%3A1%7D;",  # Thay bằng cookie Facebook của bạn
    "c_user=61576745407310;xs=1:mX-BpIZeF-XFQQ:2:1748624475:-1:-1;dpr=0.22140221297740936;locale=vi_VN;wl_cbv=v2%3Bclient_version%3A2839%3Btimestamp%3A1749362040;datr=U-Q5aE6ju_MeWbcBeo3UjUP-;sb=ZyVFaPAAk7gvctAyTkZ24CxU;ps_n=1;ps_l=1;fbl_st=101535528%3BT%3A29156034;wd=1600x753;fr=0pQfUAOZBw55GpckG.AWfn1-Sn6gYiLR2DINiQCRC_3hWytJzlJZlLgGFh15WTkYw15z4.BoRSVc..AAA.0.0.Boex_J.AWdDQr1dvJK0DGMseRqs897LHhQ;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752900131582%2C%22v%22%3A1%7D;",  # Thêm các cookie khác nếu cần
    # "cookie3",  # Bỏ comment để thêm cookie
]

def get_token(cookies):
    gome_token = []
    for cookie in cookies:
        headers = {
            'authority': 'business.facebook.com',
            'cookie': cookie,
        }
        try:
            res = requests.get('https://business.facebook.com/content_management', headers=headers).text
            token = res.split('EAAG')[1].split('","')[0]
            gome_token.append(f'{cookie}|EAAG{token}')
        except:
            pass
    return gome_token

def share(tach, id_share):
    cookie, token = tach.split('|')
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
    def share_command(message):
        try:
            # Kiểm tra tham số lệnh
            args = message.text.split()[1:]  # Bỏ phần /share
            if len(args) != 2:
                bot.reply_to(message, "Vui lòng sử dụng: /share <id> <số lượng>")
                return

            id_share = args[0]
            try:
                total_share = int(args[1])
            except ValueError:
                bot.reply_to(message, "Số lượng phải là một số nguyên.")
                return

            # Lấy token từ danh sách cookies trong code
            accounts = get_token(COOKIES)
            if not accounts:
                bot.reply_to(message, "Không có tài khoản hợp lệ.")
                return

            # Thực hiện share
            stt = 0
            while stt < total_share:
                for acc in accounts:
                    stt += 1
                    threading.Thread(target=share, args=(acc, id_share)).start()
                    bot.reply_to(message, f"[{stt}] Share thành công ID: {id_share}")
                    
                    if stt >= total_share:
                        break
                        
                    time.sleep(10)  # Delay mặc định 10 giây

            bot.reply_to(message, "Share hoàn tất!")
        except Exception as e:
            bot.reply_to(message, f"Lỗi: {str(e)}")
