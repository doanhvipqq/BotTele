import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import zipfile
import tempfile

MIN_WIDTH = 300
MIN_HEIGHT = 300

# === HỖ TRỢ ===
def is_valid_image(content):
    """Kiểm tra xem ảnh có hợp lệ và đủ kích thước không"""
    try:
        img = Image.open(BytesIO(content))
        return img.width >= MIN_WIDTH and img.height >= MIN_HEIGHT
    except:
        return False

def extract_chapter_info(url):
    """Trích xuất thông tin manga và chapter từ URL"""
    parts = url.strip('/').split('/')
    try:
        manga_slug = parts[parts.index('truyen') + 1]
        chapter_slug = parts[-1]
        return manga_slug, chapter_slug
    except Exception:
        return "unknown_manga", "unknown_chapter"

def get_manga_images(url):
    """Lấy tất cả ảnh manga từ URL"""
    try:
        # Headers để giả lập browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': url
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm ảnh trong các container phổ biến của lxmanga
        image_containers = [
            '.reading-content img',
            '.chapter-content img',
            '.manga-content img',
            '.page-chapter img',
            '#chapter-content img',
            '.entry-content img'
        ]
        
        img_tags = []
        for selector in image_containers:
            imgs = soup.select(selector)
            if imgs:
                img_tags = imgs
                break
        
        # Fallback: tìm tất cả img tags
        if not img_tags:
            img_tags = soup.find_all('img')
        
        return img_tags
        
    except Exception as e:
        print(f"Lỗi khi lấy HTML: {e}")
        return []

def register_getzip(bot):
    @bot.message_handler(commands=['getzip'])
    def handle_getzip(message):
        # Lấy URL từ tin nhắn
        url = message.text.replace('/getzip', '').strip()
        
        if not url.startswith("http"):
            bot.reply_to(message, "❌ Gửi link hợp lệ nhé bạn.\n\n📝 **Cách sử dụng:**\n`/getzip https://lxmanga.blog/truyen/manga-name/chapter`", parse_mode="Markdown")
            return
        
        # Trích xuất thông tin manga và chapter
        manga_slug, chapter_slug = extract_chapter_info(url)
        
        # Thông báo bắt đầu
        status_msg = bot.send_message(
            message.chat.id, 
            f"⏳ Đang tải ảnh: *{manga_slug} / {chapter_slug}*\n🔍 Đang phân tích trang...", 
            parse_mode="Markdown"
        )
        
        try:
            # Lấy danh sách ảnh từ trang web
            img_tags = get_manga_images(url)
            
            if not img_tags:
                bot.edit_message_text(
                    "❌ Không thể truy cập trang web.\n💡 **Thử:**\n• Kiểm tra link\n• Sử dụng VPN",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
                return
            
            # Cập nhật trạng thái
            bot.edit_message_text(
                f"⏳ Đang tải ảnh: *{manga_slug} / {chapter_slug}*\n📥 Tìm thấy {len(img_tags)} ảnh, đang tải...",
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown"
            )
            
            images = []
            valid_count = 0
            
            for i, img in enumerate(img_tags):
                # Ưu tiên lấy ảnh thực tế từ lazy-loading
                src = img.get('data-src') or img.get('data-original') or img.get('src')
                if not src:
                    continue
                
                # Chuyển đổi URL tương đối thành tuyệt đối
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)
                
                # Bỏ các ảnh không liên quan
                exclude_keywords = [
                    'logo', 'icon', 'ads', 'footer', 'spinner', 'loading', 
                    'lxmanga.com', 'banner', 'avatar', 'favicon', 'thumb'
                ]
                
                if any(keyword in src.lower() for keyword in exclude_keywords):
                    continue
                
                try:
                    # Headers cho request ảnh
                    img_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': url,
                        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
                    }
                    
                    r = requests.get(src, headers=img_headers, timeout=15)
                    r.raise_for_status()
                    
                    if is_valid_image(r.content):
                        # Đặt tên file theo thứ tự
                        filename = f'page_{valid_count + 1:03d}.jpg'
                        images.append((filename, r.content))
                        valid_count += 1
                        
                        # Cập nhật tiến độ mỗi 5 ảnh
                        if valid_count % 5 == 0:
                            bot.edit_message_text(
                                f"⏳ Đang tải ảnh: *{manga_slug} / {chapter_slug}*\n📥 Đã tải: {valid_count} ảnh hợp lệ...",
                                message.chat.id,
                                status_msg.message_id,
                                parse_mode="Markdown"
                            )
                        
                except Exception as e:
                    print(f"Lỗi tải ảnh {src}: {e}")
                    continue
            
            if not images:
                bot.edit_message_text(
                    "❌ Không tìm thấy ảnh phù hợp.\n\n💡 **Có thể do:**\n• Trang yêu cầu VPN\n• Cấu trúc web đã thay đổi\n• Ảnh bị bảo vệ",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
                return
            
            # Cập nhật trạng thái nén file
            bot.edit_message_text(
                f"⏳ Đang tải ảnh: *{manga_slug} / {chapter_slug}*\n🗜️ Đang nén {len(images)} ảnh thành ZIP...",
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown"
            )
            
            # Nén ảnh vào file zip
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
                with zipfile.ZipFile(tmp_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for filename, content in images:
                        arc_path = f"{manga_slug}/{chapter_slug}/{filename}"
                        zipf.writestr(arc_path, content)
                zip_path = tmp_zip_file.name
            
            # Kiểm tra kích thước file
            zip_size = os.path.getsize(zip_path)
            zip_size_mb = zip_size / (1024 * 1024)
            
            if zip_size_mb > 50:  # Telegram limit 50MB
                bot.edit_message_text(
                    f"❌ File quá lớn ({zip_size_mb:.1f}MB > 50MB)\n💡 **Thử tách nhỏ chapter hoặc giảm chất lượng**",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
                os.remove(zip_path)
                return
            
            # Gửi file zip cho người dùng
            with open(zip_path, 'rb') as f:
                bot.send_document(
                    message.chat.id, 
                    f, 
                    caption=f"📦 **{manga_slug} / {chapter_slug}**\n📊 {len(images)} ảnh | {zip_size_mb:.1f}MB",
                    parse_mode="Markdown"
                )
            
            # Xóa tin nhắn trạng thái
            bot.delete_message(message.chat.id, status_msg.message_id)
            
            # Xóa file tạm
            os.remove(zip_path)
            
        except Exception as e:
            bot.edit_message_text(
                f"❌ Đã xảy ra lỗi:\n`{str(e)}`\n\n💡 **Thử lại hoặc kiểm tra link**",
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown"
            )