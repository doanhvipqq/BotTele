import os
import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def register_lxmanga(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        args = message.text.split(maxsplit=1)
        if len(args) != 2 or not args[1].startswith("http"):
            bot.reply_to(message, "❗️ Bạn cần nhập đúng định dạng: /lxmanga <url chương truyện>", parse_mode="Markdown")
            return

        chap_url = args[1].strip()
        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            zip_data, total, story_name = get_zip_from_chapter(chap_url)

            if total == 0:
                bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy ảnh nào trong trang.")
                return

            zip_data.seek(0)
            file_name = story_name + ".zip"

            # Xóa tin nhắn "đang xử lý"
            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

            # Gửi file zip
            bot.send_document(
                chat_id=message.chat.id,
                document=zip_data,
                visible_file_name=file_name,
                caption=f"Đã tải xong {total} ảnh từ chương truyện!",
                reply_to_message_id=message.message_id
            )

        except Exception as e:
            bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text=f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")

    def get_zip_from_chapter(chap_url):
        headers = {
            "Referer": chap_url,
            "User-Agent": "Mozilla/5.0",
        }

        response = requests.get(chap_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Tên chương
        chapter_tag = soup.select_one("h2.chapter-title")
        chapter_name = chapter_tag.text.strip() if chapter_tag else "Chương không rõ tên"

        # Tên truyện: ưu tiên từ trang chương
        story_tag = soup.select_one("h1.story-title")
        if story_tag:
            story_name = story_tag.text.strip()
        else:
            # Nếu không có, thì lấy từ trang truyện cha
            story_url = get_main_story_url(chap_url)
            story_name = fetch_story_name_from_main_page(story_url, headers)

        # Lấy ảnh
        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for idx, img_url in enumerate(img_urls):
                ext = img_url.split(".")[-1].split("?")[0]
                filename = f"{idx+1:03d}.{ext}"
                img_data = requests.get(img_url, headers=headers).content
                zip_path = f"{story_name}/{chapter_name}/{filename}"
                zipf.writestr(zip_path, img_data)

        return zip_buffer, len(img_urls), story_name

    def get_main_story_url(chap_url):
        parsed = urlparse(chap_url)
        path_parts = parsed.path.strip("/").split("/")
        # Xử lý URL như: /truyen/ten-truyen/chap-123 -> /truyen/ten-truyen/
        if len(path_parts) >= 3:
            main_path = "/".join(path_parts[:2]) + "/"
        else:
            main_path = parsed.path  # fallback
        return urljoin(f"{parsed.scheme}://{parsed.netloc}", main_path)

    def fetch_story_name_from_main_page(story_url, headers):
        try:
            res = requests.get(story_url, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            story_tag = soup.select_one("h1.story-title")
            return story_tag.text.strip() if story_tag else "Truyện không rõ tên"
        except:
            return "Truyện không rõ tên"
