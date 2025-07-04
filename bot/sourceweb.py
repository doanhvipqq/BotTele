import os
import re
import requests
import zipfile
import tempfile
import urllib.parse
from bs4 import BeautifulSoup

def register_sourceweb(bot):
    @bot.message_handler(commands=['sourceweb'])
    def handle_sourceweb(message):
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Vui lòng cung cấp URL. Ví dụ: /sourceweb https://example.com")
            return

        url = args[1]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")

        try:
            domain = urllib.parse.urlparse(url).netloc
            zip_filename = f"{domain}_source.zip"

            with tempfile.TemporaryDirectory() as temp_dir:
                downloaded = download_website(url, temp_dir, bot, message, msg.message_id)

                if not downloaded:
                    bot.edit_message_text("🚫 Không thể tải nội dung (lỗi mạng hoặc vượt quá 50MB).", message.chat.id, msg.message_id)
                    return

                zip_path = os.path.join(temp_dir, zip_filename)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for f in downloaded:
                        rel_path = os.path.relpath(f, temp_dir)
                        zipf.write(f, rel_path)

                with open(zip_path, 'rb') as f:
                    bot.send_document(message.chat.id, f, caption=f"📦 {len(downloaded)} file từ {url}")

            bot.delete_message(message.chat.id, msg.message_id)

        except Exception as e:
            bot.edit_message_text(f"❌ Lỗi: {str(e)}", message.chat.id, msg.message_id)

    def download_website(base_url, output_dir, bot, message, msg_id, max_total_size=50 * 1024 * 1024):
        processed = set()
        files = []
        queue = [base_url]
        domain = urllib.parse.urlparse(base_url).netloc
        headers = {'User-Agent': 'Mozilla/5.0'}
        total_size = 0

        while queue:
            url = queue.pop(0)
            if url in processed:
                continue
            processed.add(url)

            if urllib.parse.urlparse(url).netloc != domain:
                continue

            try:
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code != 200:
                    continue

                # Xác định loại file và đường dẫn lưu
                ctype = res.headers.get('Content-Type', '').lower()
                path = urllib.parse.urlparse(url).path
                if not path or path.endswith('/'):
                    path += 'index.html'
                path = re.sub(r'[?#].*$', '', path)
                save_path = os.path.join(output_dir, domain, path.lstrip('/'))

                if save_path in files:
                    continue  # tránh trùng file

                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(res.content)

                file_size = os.path.getsize(save_path)
                total_size += file_size
                if total_size > max_total_size:
                    break

                files.append(save_path)

                # Nếu là HTML thì phân tích thêm liên kết
                if 'text/html' in ctype:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for tag, attr in [('link', 'href'), ('script', 'src'), ('img', 'src')]:
                        for el in soup.find_all(tag):
                            src = el.get(attr)
                            if src:
                                full_url = urllib.parse.urljoin(url, src)
                                if urllib.parse.urlparse(full_url).netloc == domain and full_url not in processed:
                                    queue.append(full_url)

            except Exception as e:
                bot.edit_message_text(f"⚠️ Lỗi khi tải {url}:\n{e}", message.chat.id, msg_id)
                return []

        return files
