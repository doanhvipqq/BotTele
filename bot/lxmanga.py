import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def register_lxmanga(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        try:
            chap_url = message.text.split(maxsplit=1)[1].strip()
            if not chap_url.startswith("https://lxmanga."):
                raise ValueError
        except (IndexError, ValueError):
            bot.reply_to(message, "❗️Bạn cần nhập đúng định dạng: `/lxmanga <url chương>`", parse_mode="Markdown")
            return

        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            zip_data, total, file_name = get_zip_from_chapter(chap_url)

            if total == 0:
                bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy ảnh nào trong trang.")
                return

            zip_data.seek(0)

            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

            bot.send_document(
                chat_id=message.chat.id,
                document=zip_data,
                visible_file_name=file_name,
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

        # Lấy tên truyện và chương từ <title>
        story_name, chapter_name = get_names_from_title(soup)

        # Cào ảnh từ div.lazy
        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for idx, img_url in enumerate(img_urls):
                ext = img_url.split(".")[-1].split("?")[0]
                filename = f"{idx+1:03d}.{ext}"

                img_data = requests.get(img_url, headers=headers, timeout=10).content

                clean_story_name = story_name.replace("(", "").replace(")", "")
                zip_path = f"{clean_story_name}/{chapter_name}/{filename}"
                zipf.writestr(zip_path, img_data)

        file_name = f"{story_name}.zip"
        return zip_buffer, len(img_urls), file_name

    def get_names_from_title(soup):
        for tag in reversed(soup.find_all("title")):
            title_text = tag.get_text(strip=True)
            if " - LXMANGA" in title_text:
                # Bỏ phần cuối
                title_text = title_text.replace(" - LXMANGA", "").strip()
                if " - " in title_text:
                    parts = title_text.split(" - ", maxsplit=1)  # chỉ tách 1 lần từ trái
                    if len(parts) == 2:
                        chapter_name = parts[0].strip()
                        story_name = parts[1].strip()
                        return story_name, chapter_name
        return "Unknown_Story", "Unknown_Chapter"