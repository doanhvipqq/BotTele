import os
import requests
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from io import BytesIO

def register_getzip(bot):
    @bot.message_handler(commands=['getzip'])
    def handle_getzip(message):
        args = message.text.split(maxsplit=1)
        if len(args) != 2 or not args[1].startswith("http"):
            bot.reply_to(message, "❗ Bạn cần nhập đúng định dạng: `/getzip <url>`", parse_mode="Markdown")
            return

        chap_url = args[1].strip()
        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            zip_data, total = get_zip_from_chapter(chap_url)

            if total == 0:
                bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy ảnh nào trong trang.")
                return

            zip_data.seek(0)
            file_name = get_story_name_from_url(chap_url) + ".zip"

            # Xóa tin nhắn "đang xử lý"
            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

            # Gửi file zip
            bot.send_document(
                chat_id=message.chat.id,
                document=zip_data,
                visible_file_name=file_name,
                caption=f"✅ Đã tải xong {total} ảnh từ chương truyện!"
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

        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]

        zip_buffer = BytesIO()

        story_name = get_story_name_from_url(chap_url)
        chapter_name = get_chapter_name_from_url(chap_url)

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for idx, img_url in enumerate(img_urls):
                ext = img_url.split(".")[-1].split("?")[0]
                filename = f"{idx+1:03d}.{ext}"

                img_data = requests.get(img_url, headers=headers).content

                # Ghi file theo cấu trúc thư mục trong zip
                zip_path = f"{story_name}/{chapter_name}/{filename}"
                zipf.writestr(zip_path, img_data)

        return zip_buffer, len(img_urls)

    def get_story_name_from_url(url):
        path_parts = urlparse(url).path.strip("/").split("/")
        # Giả sử URL kiểu /truyen/one-piece/chap-1084/
        if len(path_parts) >= 2 and path_parts[0].lower() == "truyen":
            # Thay dấu "-" bằng dấu cách
            return path_parts[1].replace("-", " ")
        else:
            # Fallback, thay "/" bằng "_"
            return urlparse(url).path.strip("/").replace("/", "_")

    def get_chapter_name_from_url(url):
        path_parts = urlparse(url).path.strip("/").split("/")
        for part in path_parts:
            if part.lower().startswith("chap"):
                return part.replace("-", " ")
        return "chapter"  # fallback