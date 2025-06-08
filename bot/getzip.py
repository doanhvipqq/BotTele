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
    """Lấy tất cả ảnh manga từ URL với xử lý chống bot"""
    import time
    
    # Danh sách User-Agent để thử
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
    for attempt, ua in enumerate(user_agents):
        try:
            print(f"Thử lần {attempt + 1} với User-Agent: {ua[:50]}...")
            
            # Session với cookie support
            session = requests.Session()
            
            # Headers giả lập browser thực
            headers = {
                'User-Agent': ua,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # Thêm delay ngẫu nhiên để tránh bị phát hiện
            time.sleep(2 + attempt)
            
            # Request đầu tiên để lấy cookie
            response = session.get(url, headers=headers, timeout=20, allow_redirects=True)
            
            # Kiểm tra status code
            if response.status_code == 403:
                print(f"Bị chặn 403, thử User-Agent khác...")
                continue
            elif response.status_code == 503:
                print(f"Server quá tải 503, chờ thêm...")
                time.sleep(5)
                continue
            elif response.status_code != 200:
                print(f"Status code: {response.status_code}")
                continue
            
            # Kiểm tra xem có phải trang Cloudflare không
            if 'cloudflare' in response.text.lower() or 'checking your browser' in response.text.lower():
                print("Phát hiện Cloudflare protection, thử cách khác...")
                time.sleep(5)
                continue
            
            # Kiểm tra xem có nội dung không
            if len(response.text) < 1000:
                print("Nội dung quá ngắn, có thể bị chặn...")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: In title để kiểm tra
            title = soup.find('title')
            if title:
                print(f"Trang title: {title.get_text()[:100]}")
            
            # Tìm ảnh trong các container phổ biến của lxmanga
            image_selectors = [
                # Selector chính cho lxmanga
                '.reading-content img',
                '.chapter-content img', 
                '.manga-content img',
                '.page-chapter img',
                '#chapter-content img',
                '.entry-content img',
                'div[id*="chapter"] img',
                'div[class*="page"] img',
                'div[class*="reading"] img',
                # Selector backup
                'img[src*="wp-content"]',
                'img[data-src*="wp-content"]',
                'img[src*="uploads"]',
                'img[data-src*="uploads"]'
            ]
            
            img_tags = []
            for selector in image_selectors:
                imgs = soup.select(selector)
                if imgs:
                    print(f"Tìm thấy {len(imgs)} ảnh với selector: {selector}")
                    img_tags = imgs
                    break
            
            # Fallback: tìm tất cả img tags
            if not img_tags:
                print("Fallback: tìm tất cả img tags...")
                all_imgs = soup.find_all('img')
                print(f"Tổng số img tags: {len(all_imgs)}")
                
                # Debug: In ra một vài src để kiểm tra
                for i, img in enumerate(all_imgs[:5]):
                    src = img.get('data-src') or img.get('data-original') or img.get('src')
                    print(f"IMG {i+1}: {src}")
                
                # Lọc img có pattern manga
                img_tags = [img for img in all_imgs if has_manga_src(img)]
                print(f"Img tags sau khi lọc: {len(img_tags)}")
            
            if img_tags:
                return img_tags
            else:
                print("Không tìm thấy img tags, thử User-Agent khác...")
                continue
                
        except requests.exceptions.Timeout:
            print(f"Timeout lần {attempt + 1}")
            continue
        except requests.exceptions.ConnectionError:
            print(f"Connection error lần {attempt + 1}")
            continue
        except Exception as e:
            print(f"Lỗi lần {attempt + 1}: {e}")
            continue
    
    print("Đã thử hết tất cả User-Agent")
    return []

def has_manga_src(img_tag):
    """Kiểm tra xem img tag có chứa src của ảnh manga không"""
    src = img_tag.get('data-src') or img_tag.get('data-original') or img_tag.get('src') or ''
    
    if not src:
        return False
    
    # Các pattern thường thấy trong URL ảnh manga
    manga_patterns = [
        '/wp-content/uploads/',
        '/images/manga/',
        '/chapter/',
        '/page/',
        'uploads/',
        'manga',
        'chapter'
    ]
    
    # Kiểm tra file extension
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    has_image_ext = any(ext in src.lower() for ext in image_extensions)
    
    # Kiểm tra pattern manga
    has_manga_pattern = any(pattern in src.lower() for pattern in manga_patterns)
    
    # Loại bỏ các ảnh rõ ràng không phải manga
    exclude_patterns = [
        'logo', 'icon', 'favicon', 'avatar', 'banner', 
        'ads', 'advertisement', 'social', 'footer',
        'lxmanga.com/wp-content/themes',  # Theme assets
        'lxmanga.com/wp-includes',       # WordPress core
        'loading', 'spinner', 'preload'
    ]
    
    is_excluded = any(pattern in src.lower() for pattern in exclude_patterns)
    
    # Debug log
    if has_image_ext and has_manga_pattern and not is_excluded:
        print(f"✅ Valid manga src: {src[:80]}...")
    elif is_excluded:
        print(f"❌ Excluded src: {src[:80]}...")
    
    return has_image_ext and has_manga_pattern and not is_excluded

def is_loading_gif(src, content=None):
    """Kiểm tra xem có phải ảnh loading/gif không"""
    if not src:
        return False
        
    # Kiểm tra URL chứa từ khóa loading
    loading_keywords = [
        'loading', 'spinner', 'load', 'wait', 'preload',
        'lxmanga.com', 'lxers', 'logo', 'watermark',
        'gif', 'placeholder', 'lazy'
    ]
    
    src_lower = src.lower()
    if any(keyword in src_lower for keyword in loading_keywords):
        return True
    
    # Kiểm tra content nếu có
    if content:
        try:
            img = Image.open(BytesIO(content))
            # Ảnh loading thường có kích thước nhỏ và là GIF
            if img.format == 'GIF' and (img.width < 200 or img.height < 200):
                return True
            # Ảnh có kích thước giống logo lxmanga
            if img.width == img.height and img.width < 300:
                return True
        except:
            pass
    
    return False

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
            
            # Cập nhật trạng thái với thông tin debug
            bot.edit_message_text(
                f"⏳ Đang tải ảnh: *{manga_slug} / {chapter_slug}*\n🔍 Tìm thấy {len(img_tags)} ảnh tiềm năng...\n📝 Đang phân tích từng ảnh...",
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
                
                # KIỂM TRA QUAN TRỌNG: Bỏ qua ảnh loading/gif
                if is_loading_gif(src):
                    print(f"Bỏ qua ảnh loading: {src}")
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
                    
                    # Kiểm tra kép: cả URL và nội dung
                    if is_loading_gif(src, r.content):
                        print(f"Bỏ qua ảnh loading (sau khi tải): {src}")
                        continue
                    
                    if is_valid_image(r.content):
                        # Kiểm tra cuối: đảm bảo không phải ảnh vuông nhỏ (logo)
                        try:
                            img = Image.open(BytesIO(r.content))
                            # Bỏ ảnh vuông có kích thước nhỏ (thường là logo)
                            if img.width == img.height and img.width < 400:
                                print(f"Bỏ qua logo/ảnh vuông: {src} ({img.width}x{img.height})")
                                continue
                            # Ảnh manga thường có tỷ lệ dọc
                            if img.height < img.width * 0.8:  # Quá ngang, có thể là banner
                                print(f"Bỏ qua ảnh ngang: {src} ({img.width}x{img.height})")
                                continue
                        except:
                            pass
                        
                        # Đặt tên file theo thứ tự
                        filename = f'page_{valid_count + 1:03d}.jpg'
                        images.append((filename, r.content))
                        valid_count += 1
                        print(f"Đã tải ảnh hợp lệ: {src}")
                        
                        # Cập nhật tiến độ mỗi 3 ảnh (để người dùng thấy tiến độ)
                        if valid_count % 3 == 0:
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