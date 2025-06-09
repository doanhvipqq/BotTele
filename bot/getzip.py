import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm
from io import BytesIO

def register_getzip(bot):
    @bot.message_handler(commands=['getzip'])
    def handle_getzip(message):
        args = message.text.split(maxsplit=1)
        if len(args) != 2 or not args[1].startswith("http"):
            bot.reply_to(message, "❗ Bạn cần nhập đúng định dạng: `/getzip <url>`", parse_mode="Markdown")
            return
    
        chap_url = args[1].strip()
        bot.reply_to(message, f"🔄 Đang tải ảnh từ:\n{chap_url}")
    
        try:
            zip_data, total = get_zip_from_chapter(chap_url)
    
            if total == 0:
                bot.send_message(message.chat.id, "❌ Không tìm thấy ảnh nào trong trang.")
                return
    
            zip_data.seek(0)
            file_name = urlparse(chap_url).path.strip("/").replace("/", "_") + ".zip"
    
            bot.send_document(
                message.chat.id,
                zip_data,
                visible_file_name=file_name,
                caption=f"✅ Tải xong {total} ảnh từ chương truyện!",
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")
    
    
    def get_zip_from_chapter(chap_url):
        headers = {
            "Referer": chap_url,
            "User-Agent": "Mozilla/5.0",
        }
    
        response = requests.get(chap_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    
        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]
    
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for idx, img_url in enumerate(tqdm(img_urls, desc="Zipping images")):
                ext = img_url.split(".")[-1].split("?")[0]
                filename = f"{idx+1:03d}.{ext}"
    
                img_data = requests.get(img_url, headers=headers).content
                zipf.writestr(filename, img_data)
    
        return zip_buffer, len(img_urls)