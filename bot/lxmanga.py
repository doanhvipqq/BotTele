import os
import zipfile
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def register_lxmanga_multi(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        args = message.text.split(maxsplit=1)
        if len(args) != 2 or not args[1].startswith("http"):
            bot.reply_to(message, "❗ Bạn cần nhập đúng định dạng: `/lxmanga <url-truyen>`", parse_mode="Markdown")
            return

        story_url = args[1].strip()
        sent_msg = bot.reply_to(message, "🔍 Đang lấy danh sách chương...")

        try:
            chapter_urls = get_chapter_urls(story_url)
            if not chapter_urls:
                bot.edit_message_text(sent_msg.chat.id, sent_msg.message_id, "❌ Không tìm thấy chương nào.")
                return

            bot.edit_message_text(sent_msg.chat.id, sent_msg.message_id, f"📥 Đang tải {len(chapter_urls)} chương...")

            zip_img_buffer = BytesIO()
            zip_pdf_buffer = BytesIO()

            with zipfile.ZipFile(zip_img_buffer, "w") as zip_img, zipfile.ZipFile(zip_pdf_buffer, "w") as zip_pdf:
                for chap_url in chapter_urls:
                    chapter_name, img_datas = get_chapter_images(chap_url)
                    if not img_datas:
                        continue

                    # Ghi vào zip ảnh
                    for i, img_bytes in enumerate(img_datas):
                        zip_img.writestr(f"{chapter_name}/{i+1:03d}.jpg", img_bytes)

                    # Ghi PDF
                    pdf_bytes = make_pdf(img_datas)
                    zip_pdf.writestr(f"{chapter_name}.pdf", pdf_bytes)

            zip_img_buffer.seek(0)
            zip_pdf_buffer.seek(0)
            story_name = get_story_name_from_url(story_url)

            bot.send_document(message.chat.id, zip_img_buffer, visible_file_name=f"{story_name}_images.zip")
            bot.send_document(message.chat.id, zip_pdf_buffer, visible_file_name=f"{story_name}_pdfs.zip")

        except Exception as e:
            bot.edit_message_text(sent_msg.chat.id, sent_msg.message_id, f"❌ Lỗi: `{str(e)}`", parse_mode="Markdown")

    def get_chapter_urls(story_url):
        res = requests.get(story_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        chap_links = soup.select(".works-chapter-list a")
        urls = [a['href'] for a in chap_links if a['href'].startswith("http")]
        return urls[::-1]  # đảo ngược để từ chap đầu đến chap mới

    def get_chapter_images(chap_url):
        res = requests.get(chap_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]
        images = []
        for url in img_urls:
            try:
                img = requests.get(url, timeout=10).content
                images.append(img)
            except:
                continue
        return get_chapter_name_from_url(chap_url), images

    def make_pdf(img_datas):
        imgs = [Image.open(BytesIO(data)).convert("RGB") for data in img_datas]
        if not imgs:
            return b''
        pdf_buffer = BytesIO()
        imgs[0].save(pdf_buffer, format="PDF", save_all=True, append_images=imgs[1:])
        pdf_buffer.seek(0)
        return pdf_buffer.read()

    def get_story_name_from_url(url):
        parts = urlparse(url).path.strip("/").split("/")
        return parts[1].replace("-", " ") if len(parts) > 1 else "story"

    def get_chapter_name_from_url(url):
        parts = urlparse(url).path.strip("/").split("/")
        for p in parts:
            if "chap" in p.lower():
                return p.replace("-", " ")
        return "unknown-chapter"
