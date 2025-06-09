import zipfile
import requests
import cloudscraper
from io import BytesIO
from bs4 import BeautifulSoup

def register_lxmanga(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        args = message.text.split(maxsplit=1)
        if len(args) != 2 or not args[1].startswith("http"):
            bot.reply_to(message, "❗ Vui lòng nhập: /lxmanga <url>", parse_mode="Markdown")
            return

        chap_url = args[1].strip()
        sent_msg = bot.reply_to(message, "🔍 Đang xử lý...")

        try:
            zip_data, total = get_zip_from_chapter(chap_url)
            if total == 0:
                bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy ảnh.")
                return

            zip_data.seek(0)
            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
            bot.send_document(
                chat_id=message.chat.id,
                document=zip_data,
                visible_file_name="chapter.zip",
                caption=f"Tải thành công {total} ảnh!",
                reply_to_message_id=message.message_id
            )
        except Exception as e:
            bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text=f"❌ Lỗi: {str(e)}", parse_mode="Markdown")

def get_zip_from_chapter(chap_url):
    headers = {"Referer": chap_url, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
    scraper = cloudscraper.create_scraper()
    
    # Thử dùng requests trước
    try:   
        response = requests.get(chap_url, headers=headers, timeout=10)
        response.raise_for_status()
    except:
        # Dự phòng dùng cloudscraper
        response = scraper.get(chap_url, headers=headers, timeout=10)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    img_urls = [div["data-src"] for div in soup.select("div.text-center div.lazy") if div.get("data-src")]

    zip_buffer = BytesIO()
    story_name = soup.select_one("div.mb-4 span") or "Manga"
    story_name = story_name.text.strip().replace("/", "_") if isinstance(story_name, BeautifulSoup) else story_name
    chapter_name = soup.select_one("span.text-ellipsis") or "Chapter"
    chapter_name = chapter_name.text.strip().replace("/", "_") if isinstance(chapter_name, BeautifulSoup) else chapter_name

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, img_url in enumerate(img_urls):
            ext = img_url.split(".")[-1].split("?")[0]
            try:
                # Tải ảnh với cloudscraper hoặc requests
                img_response = requests.get(img_url, headers=headers, timeout=5)
                if "image" not in img_response.headers.get("Content-Type", ""):
                    continue
                img_data = img_response.content
            except:
                img_response = scraper.get(img_url, headers=headers, timeout=5)
                if "image" not in img_response.headers.get("Content-Type", ""):
                    continue
                img_data = img_response.content

            zip_path = f"{story_name}/{chapter_name}/{idx+1:03d}.{ext}"
            zipf.writestr(zip_path, img_data)

    return zip_buffer, len(img_urls)
