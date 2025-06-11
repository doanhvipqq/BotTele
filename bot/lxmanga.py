import os
import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telebot import types

def register_lxmanga(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        args = message.text.split(maxsplit=1)
        if len(args) != 2 or not args[1].startswith("http"):
            bot.reply_to(message, "❗️ Bạn cần nhập đúng định dạng: /lxmanga <url truyện>", parse_mode="Markdown")
            return

        url = args[1].strip()
        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            if is_chapter_url(url):
                zip_data, story_name, chapter_name, total = get_zip_from_chapter(url)

                if total == 0:
                    bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy ảnh nào trong chương.")
                    return

                zip_data.seek(0)
                file_name = f"{story_name} - {chapter_name}.zip"

                bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)
                bot.send_document(
                    chat_id=message.chat.id,
                    document=zip_data,
                    visible_file_name=file_name,
                    caption=f"✅ Đã tải xong chương *{chapter_name}* của *{story_name}* ({total} ảnh)!",
                    parse_mode="Markdown",
                    reply_to_message_id=message.message_id
                )
            else:
                chapters, story_title = get_chapters_from_story(url)
                if not chapters:
                    bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy chương nào.")
                    return

                markup = types.InlineKeyboardMarkup()
                for chap_name, chap_link in chapters:
                    markup.add(types.InlineKeyboardButton(text=chap_name, callback_data=f"lxmanga|{chap_link}"))

                bot.edit_message_text(
                    chat_id=sent_msg.chat.id,
                    message_id=sent_msg.message_id,
                    text=f"📚 *{story_title}*\nVui lòng chọn chương muốn tải:",
                    parse_mode="Markdown",
                    reply_markup=markup
                )
        except Exception as e:
            bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text=f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lxmanga|"))
    def callback_download_chapter(call):
        chap_url = call.data.split("|", 1)[1]
        try:
            zip_data, story_name, chapter_name, total = get_zip_from_chapter(chap_url)
            if total == 0:
                bot.answer_callback_query(call.id, "❌ Không tìm thấy ảnh.")
                return

            zip_data.seek(0)
            file_name = f"{story_name} - {chapter_name}.zip"

            bot.send_document(
                chat_id=call.message.chat.id,
                document=zip_data,
                visible_file_name=file_name,
                caption=f"✅ Đã tải xong chương *{chapter_name}* của *{story_name}* ({total} ảnh)!",
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Lỗi: {str(e)}")

    def is_chapter_url(url):
        return "/chap-" in url or "/chapter-" in url or "/oneshot" in url

    def get_chapters_from_story(story_url):
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        response = requests.get(story_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title_el = soup.select_one("h1")
        story_title = title_el.text.strip() if title_el else "Không rõ tên truyện"

        chapter_links = soup.select("div.list-chapter a")
        chapters = []
        for a in chapter_links:
            chap_name = a.text.strip()
            chap_href = a.get("href")
            if chap_href:
                full_link = chap_href if chap_href.startswith("http") else f"https://lxmanga.blog{chap_href}"
                chapters.append((chap_name, full_link))

        return chapters, story_title

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

        story_name = soup.select_one("ol.breadcrumb a:nth-last-child(2)")
        chapter_name = soup.select_one("ol.breadcrumb li.active")
        story_title = story_name.text.strip() if story_name else "Truyen khong ro ten"
        chapter_title = chapter_name.text.strip() if chapter_name else "Chuong khong ro ten"

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for idx, img_url in enumerate(img_urls):
                ext = img_url.split(".")[-1].split("?")[0]
                filename = f"{idx+1:03d}.{ext}"
                img_data = requests.get(img_url, headers=headers).content
                zip_path = f"{story_title}/{chapter_title}/{filename}"
                zipf.writestr(zip_path, img_data)

        return zip_buffer, story_title, chapter_title, len(img_urls)
