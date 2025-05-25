import re
import requests
from bs4 import BeautifulSoup

def register_images(bot):
    @bot.message_handler(commands=['images'])
    def images(message):
        # Tách các tham số sau lệnh, ví dụ: "/images https://example.com"
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, 'Vui lòng cung cấp URL. Ví dụ: /images https://example.com')
            return

        url = args[0]
        # Kiểm tra URL có bắt đầu bằng http:// hoặc https:// không
        if not re.match(r'^https?://', url):
            bot.reply_to(message, 'URL không hợp lệ. Hãy bắt đầu bằng http:// hoặc https://')
            return

        bot.reply_to(message, f'Đang tải trang: {url} ...')
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()  # Kiểm tra lỗi HTTP
        except Exception as e:
            bot.reply_to(message, f'Không thể tải trang: {e}')
            return

        soup = BeautifulSoup(resp.text, 'html.parser')
        image_urls = []

        # Lấy các URL từ thẻ <img>
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = requests.compat.urljoin(resp.url, src)
                image_urls.append(full_url)

        # Lấy URL từ thuộc tính style (ví dụ: background-image)
        for tag in soup.find_all(style=True):
            style = tag['style']
            matches = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
            for match in matches:
                full_url = requests.compat.urljoin(resp.url, match)
                image_urls.append(full_url)

        if not image_urls:
            bot.reply_to(message, 'Không tìm thấy ảnh nào trên trang.')
            return

        # Đánh số các URL, chia theo nhóm (mỗi tin nhắn tối đa 30 dòng)
        numbered = [f"{i+1}. {img_url}" for i, img_url in enumerate(image_urls)]
        batch_size = 30
        for i in range(0, len(numbered), batch_size):
            chunk = "\n".join(numbered[i:i+batch_size])
            bot.reply_to(message, chunk, disable_web_page_preview=True)