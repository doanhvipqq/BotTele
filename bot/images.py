import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def register_images(bot):
    @bot.message_handler(commands=['images'])
    def images(message):
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, '🚫Vui lòng cung cấp URL.\n Ví dụ: /images https://example.com')
            return

        url = args[1]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        loading_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            resp = requests.get(url, timeout=10, headers=HEADERS)
            resp.raise_for_status()
        except Exception as e:
            bot.reply_to(message, f'Không thể tải trang: {e}')
            return

        bot.delete_message(message.chat.id, loading_msg.message_id)

        soup = BeautifulSoup(resp.text, 'html.parser')
        image_urls = []

        # Từ <img>
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = requests.compat.urljoin(resp.url, src.strip('"\' '))
                if full_url not in image_urls:
                    image_urls.append(full_url)

        # Từ style="background-image: url(...)"
        for tag in soup.find_all(style=True):
            style = tag['style']
            matches = re.findall(r'url\((["\']?)(.*?)\1\)', style)
            for match in matches:
                full_url = requests.compat.urljoin(resp.url, match.strip('"\' '))
                if full_url not in image_urls:
                    image_urls.append(full_url)

        if not image_urls:
            bot.reply_to(message, 'Không tìm thấy url ảnh nào trên trang.')
            return

        numbered = [f"{i+1}. {img_url}" for i, img_url in enumerate(image_urls)]
        batch_size = 30
        for i in range(0, len(numbered), batch_size):
            chunk = "\n".join(numbered[i:i+batch_size])
            bot.reply_to(message, chunk, disable_web_page_preview=True)