import os
import re
import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telebot.types import InputFile

def register_lxmanga(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        try:
            chap_url = message.text.split(maxsplit=1)[1].strip()
            if not chap_url.startswith("https://lxmanga."):
                raise ValueError
        except:
            return bot.reply_to(message, "❗️Bạn cần nhập đúng định dạng: `/lxmanga <url chương>`", parse_mode="Markdown")

        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            zip_data, total, file_name = get_zip_from_chapter(chap_url)

            if total == 0:
                return bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
                                             text="❌ Không tìm thấy ảnh nào trong trang.")

            zip_data.seek(0)
            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

            bot.send_document(
                chat_id=message.chat.id,
                document=InputFile(zip_data, file_name),
                caption=f"Đã tải xong `{total}` ảnh từ chương truyện!",
                reply_to_message_id=message.message_id,
                parse_mode="Markdown"
            )

        except Exception as e:
            bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
                                  text=f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")

    def get_zip_from_chapter(chap_url):
        headers = {
            "Referer": chap_url,
            "User-Agent": "Mozilla/5.0",
        }

        response = requests.get(chap_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        story_name, chapter_name = get_names_from_title(soup)

        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for idx, img_url in enumerate(img_urls):
                try:
                    ext = os.path.splitext(urlparse(img_url).path)[1].lstrip(".") or "jpg"
                    filename = f"{idx+1:03d}.{ext}"
                    zip_path = f"{sanitize_path(story_name)}/{chapter_name}/{filename}"
                    img_data = requests.get(img_url, headers=headers, timeout=10).content
                    zipf.writestr(zip_path, img_data)
                except:
                    continue

        return zip_buffer, len(img_urls), f"{story_name}.zip"

    def get_names_from_title(soup):
        title_tag = soup.find("title")
        if not title_tag:
            return "Unknown", "Unknown"

        raw_title = title_tag.get_text(strip=True)
        if "-" not in raw_title:
            return raw_title, "Chapter"

        split_idx = raw_title.rfind("-")
        story_name = raw_title[:split_idx].strip()
        chapter_name = raw_title[split_idx + 1:].strip()
        return story_name, chapter_name

    def sanitize_path(name):
        return re.sub(r'[\\/:"*?<>|]', "_", name).strip()