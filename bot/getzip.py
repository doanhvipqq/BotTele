import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import zipfile
import tempfile

MIN_WIDTH = 300
MIN_HEIGHT = 300

# === HỖ TRỢ ===
def is_valid_image(content):
    try:
        img = Image.open(BytesIO(content))
        return img.width >= MIN_WIDTH and img.height >= MIN_HEIGHT
    except:
        return False

def extract_chapter_info(url):
    parts = url.strip('/').split('/')
    try:
        manga_slug = parts[parts.index('truyen') + 1]
        chapter_slug = parts[-1]
        return manga_slug, chapter_slug
    except Exception:
        return "unknown_manga", "unknown_chapter"
        
def register_getzip(bot):
    @bot.message_handler(commands=['getzip'])
    def handle_getzip(message):
        url = message.text.replace('/getzip', '').strip()
        if not url.startswith("http"):
            bot.reply_to(message, "❌ Gửi link hợp lệ nhé bạn.")
            return

        manga_slug, chapter_slug = extract_chapter_info(url)
        bot.send_message(message.chat.id, f"⏳ Đang tải ảnh: *{manga_slug} / {chapter_slug}*", parse_mode="Markdown")

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tags = soup.find_all('img')

            images = []
            for i, img in enumerate(img_tags):
                # Ưu tiên lấy ảnh thực tế từ lazy-loading
                src = img.get('data-src') or img.get('data-original') or img.get('src')
                if not src:
                    continue
                # Bỏ các ảnh không liên quan
                if any(x in src.lower() for x in ['logo', 'icon', 'ads', 'footer', 'spinner', 'loading', 'lxmanga.com']):
                    continue
                try:
                    r = requests.get(src, timeout=10)
                    if is_valid_image(r.content):
                        images.append((f'image_{i + 1}.jpg', r.content))
                except:
                    continue

            if not images:
                bot.reply_to(message, "❌ Không tìm thấy ảnh phù hợp.")
                return

            # Nén ảnh vào file zip
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
                with zipfile.ZipFile(tmp_zip_file, 'w') as zipf:
                    for filename, content in images:
                        arc_path = f"{manga_slug}/{chapter_slug}/{filename}"
                        zipf.writestr(arc_path, content)
                zip_path = tmp_zip_file.name

            # Gửi file zip cho người dùng
            with open(zip_path, 'rb') as f:
                bot.send_document(message.chat.id, f, caption=f"📦 *{manga_slug} / {chapter_slug}*", parse_mode="Markdown")

            os.remove(zip_path)

        except Exception as e:
            bot.reply_to(message, f"❌ Đã xảy ra lỗi:\n`{e}`", parse_mode="Markdown")