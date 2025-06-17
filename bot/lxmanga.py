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
        except Exception:
            return bot.reply_to(message, "❗️Bạn cần nhập đúng định dạng: `/lxmanga <url chương>`", parse_mode="Markdown")

        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            zip_data, total, story_name, chapter_name = get_zip_from_chapter(chap_url)

            if total == 0:
                return bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id,
                                             text="❌ Không tìm thấy ảnh nào trong trang.")

            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

            safe_file_name = make_safe_filename(story_name) + ".zip"

            bot.send_document(
                chat_id=message.chat.id,
                document=InputFile(zip_data, safe_file_name),
                caption=f"📦 `{total}` ảnh từ chương `{chapter_name}` của truyện:\n*{story_name}*",
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
                    ext = urlparse(img_url).path.split(".")[-1].split("?")[0] or "jpg"
                    filename = f"{idx+1:03d}.{ext}"
                    zip_path = f"{sanitize_zip_part(story_name)}/{sanitize_zip_part(chapter_name)}/{filename}"
                    img_data = requests.get(img_url, headers=headers, timeout=10).content
                    zipf.writestr(zip_path, img_data)
                except Exception:
                    continue

        zip_buffer.seek(0)
        return zip_buffer, len(img_urls), story_name, chapter_name

    def get_names_from_title(soup):
        title_tag = soup.find("title")
        if not title_tag:
            return "Unknown", "Unknown"

        raw_title = title_tag.get_text(strip=True)
        if "-" in raw_title:
            split_idx = raw_title.rfind("-")
            story_name = raw_title[:split_idx].strip()
            chapter_name = raw_title[split_idx + 1:].strip()
            return story_name, chapter_name

        return raw_title.strip(), "Chapter"

    def make_safe_filename(name):
        return re.sub(r'[\\/:"*?<>|]', "_", name).strip()

    def sanitize_zip_part(name):
        return re.sub(r'[\\:*?"<>|]', "_", name).strip()