import requests
import threading
import time

# Danh sách cookies, nhập trực tiếp ở đây
COOKIES = [
    "c_user=61576745407310;xs=1:mX-BpIZeF-XFQQ:2:1748624475:-1:-1;dpr=0.22140221297740936;locale=vi_VN;wl_cbv=v2%3Bclient_version%3A2839%3Btimestamp%3A1749362040;datr=U-Q5aE6ju_MeWbcBeo3UjUP-;sb=ZyVFaPAAk7gvctAyTkZ24CxU;ps_n=1;ps_l=1;fbl_st=101535528%3BT%3A29156034;wd=1600x753;fr=0pQfUAOZBw55GpckG.AWfn1-Sn6gYiLR2DINiQCRC_3hWytJzlJZlLgGFh15WTkYw15z4.BoRSVc..AAA.0.0.Boex_J.AWdDQr1dvJK0DGMseRqs897LHhQ;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752900131582%2C%22v%22%3A1%7D;",
    "c_user=61576745407310;xs=1:mX-BpIZeF-XFQQ:2:1748624475:-1:-1;dpr=0.22140221297740936;locale=vi_VN;wl_cbv=v2%3Bclient_version%3A2839%3Btimestamp%3A1749362040;datr=U-Q5aE6ju_MeWbcBeo3UjUP-;sb=ZyVFaPAAk7gvctAyTkZ24CxU;ps_n=1;ps_l=1;fbl_st=101535528%3BT%3A29156034;wd=1600x753;fr=0pQfUAOZBw55GpckG.AWfn1-Sn6gYiLR2DINiQCRC_3hWytJzlJZlLgGFh15WTkYw15z4.BoRSVc..AAA.0.0.Boex_J.AWdDQr1dvJK0DGMseRqs897LHhQ;presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1752900131582%2C%22v%22%3A1%7D;",
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

            # Gửi tin nhắn ban đầu để chỉnh sửa
            status_message = bot.reply_to(message, f"Đang bắt đầu share... [0/{total_share}]")

            # Thực hiện share
            stt = 0
            while stt < total_share:
                for acc in accounts:
                    stt += 1
                    threading.Thread(target=share, args=(acc, id_share)).start()
                    # Chỉnh sửa tin nhắn hiện tại
                    try:
                        bot.edit_message_text(
                            text=f"[{stt}/{total_share}] Share thành công ID: {id_share}",
                            chat_id=status_message.chat.id,
                            message_id=status_message.message_id
                        )
                    except:
                        pass  # Bỏ qua lỗi nếu không thể chỉnh sửa

                    if stt >= total_share:
                        break

                    time.sleep(10)  # Delay mặc định 10 giây

            # Cập nhật tin nhắn cuối cùng
            bot.edit_message_text(
                text=f"Share hoàn tất! [{stt}/{total_share}]",
                chat_id=status_message.chat.id,
                message_id=status_message.message_id
            )

        except Exception as e:
            bot.reply_to(message, f"Lỗi: {str(e)}")
