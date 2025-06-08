import zipfile
import requests
from io import BytesIO
from bs4 import BeautifulSoup

BASE_URL = "https://lxmanga.blog"

def get_manga_title(soup):
    return soup.select_one("div.mb-4 span").text.strip()

def get_chapter_list(soup):
    return [
        BASE_URL + a['href']
        for a in soup.select("ul.overflow-y-auto.overflow-x-hidden > a")
    ]

def get_image_links(soup):
    return [
        img["data-src"]
        for img in soup.select("div.text-center div.lazy")
        if img.has_attr("data-src")
    ]

def download_and_zip_images(image_urls, zip_filename):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, img_url in enumerate(image_urls):
            try:
                img_data = requests.get(img_url).content
                ext = img_url.split('.')[-1].split('?')[0]
                zipf.writestr(f"{idx+1:03d}.{ext}", img_data)
            except Exception as e:
                print(f"❌ Lỗi tải ảnh {img_url}: {e}")
    zip_buffer.seek(0)
    return zip_buffer

def get_zip_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    if "/truyen/" in url and not "/chap-" in url:
        # URL của truyện
        title = get_manga_title(soup)
        chapter_links = get_chapter_list(soup)
        all_images = []

        for chapter_url in chapter_links:
            chapter_response = requests.get(chapter_url)
            chapter_soup = BeautifulSoup(chapter_response.content, "html.parser")
            all_images += get_image_links(chapter_soup)

        filename = f"{title}.zip"
        zip_file = download_and_zip_images(all_images, filename)

    elif "/chap-" in url:
        # URL chương cụ thể
        title = get_manga_title(soup)
        chapter_name = soup.select_one("span.text-ellipsis")
        chapter_name = chapter_name.text.strip() if chapter_name else "chương"

        images = get_image_links(soup)
        filename = f"{title} | {chapter_name}.zip"
        zip_file = download_and_zip_images(images, filename)

    else:
        raise ValueError("URL không hợp lệ hoặc không phải từ lxmanga.blog")

    return filename, zip_file

def register_getzip(bot):
    @bot.message_handler(commands=['getzip'])
    def handle_getzip(message):
        try:
            args = message.text.split(" ", 1)
            if len(args) < 2:
                bot.reply_to(message, "❗ Bạn cần nhập URL sau lệnh /getzip.")
                return
    
            url = args[1].strip()
            bot.send_message(message.chat.id, "🔍 Đang xử lý, vui lòng chờ...")
    
            filename, zip_data = get_zip_from_url(url)
    
            bot.send_document(message.chat.id, zip_data, visible_file_name=filename, caption=f"✅ Đã tải xong: {filename}")
    
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Đã xảy ra lỗi: {str(e)}")