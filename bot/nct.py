import re
import json
import random
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# Cấu hình logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Thông tin API NhacCuaTui
BASE_URL = 'https://www.nhaccuatui.com'
API_SEARCH = BASE_URL + '/tim-kiem/bai-hat'

# Lưu tạm dữ liệu cho mỗi lần tìm kiếm
nct_data = {}

# User-Agent để tránh chặn
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]
ACCEPT_LANGUAGES = ["en-US,en;q=0.9", "fr-FR,fr;q=0.9", "es-ES,es;q=0.9", "de-DE,de;q=0.9", "zh-CN,zh;q=0.9"]

# Tạo headers ngẫu nhiên
def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES),
        'Referer': BASE_URL,
    }

# 1. Tìm kiếm bài hát, trả về danh sách track với title, artist, id, detail_url
def search_nhaccuatui(keyword, limit=10):
    params = {'q': keyword, 'b': 'keyword', 'l': 'tat-ca', 's': 'default'}
    try:
        resp = requests.get(API_SEARCH, params=params, headers=get_headers())
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Lỗi request khi tìm kiếm: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('ul.sn_search_returns_list_song li.sn_search_single_song')[:limit]
    tracks = []
    for item in items:
        title_elem = item.select_one('h3.title_song a')
        artist_elem = item.select_one('h4.singer_song')
        detail_href = title_elem.get('href') if title_elem else None
        if title_elem and detail_href:
            track_id = detail_href.split('.')[-2]
            title = title_elem.get_text(separator=' ', strip=True)
            artist = 'Unknown'
            if artist_elem:
                artist_links = artist_elem.select('a')
                if artist_links:
                    artists = [a.get_text(separator=' ', strip=True) for a in artist_links]
                    artist = ', '.join(artists)
                else:
                    artist = artist_elem.get_text(separator=' ', strip=True)
            tracks.append({
                'title': title,
                'artist': artist,
                'id': track_id,
                'detail_url': urljoin(BASE_URL, detail_href)
            })
    return tracks

# 2. Lấy URL audio từ trang chi tiết qua XML API
def get_download_url(track):
    detail_url = track.get('detail_url')
    if not detail_url:
        return None

    try:
        resp = requests.get(detail_url, headers=get_headers())
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Lỗi request đến trang chi tiết ({detail_url}): {e}")
        return None

    # Trích thumbnail
    try:
        soup = BeautifulSoup(html, 'html.parser')
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image and og_image.has_attr('content'):
            thumb_url = og_image['content'].strip()
            if thumb_url.startswith('//'):
                thumb_url = 'https:' + thumb_url
            track['thumbnail'] = thumb_url
    except Exception as e:
        logging.warning(f"Không lấy được thumbnail từ {detail_url}: {e}")
        track['thumbnail'] = None

    # Tìm flashData qua regex thay vì find()
    try:
        match = re.search(r'var\s+flashData\s*=\s*"(.+?)";', html)
        if not match:
            logging.warning(f"Không tìm thấy flashData trong trang: {detail_url}")
            return None

        flash_data_raw = match.group(1).encode('utf-8').decode('unicode_escape')
        flash_data = json.loads(flash_data_raw)

        # Lấy URL bài hát
        audio_url = flash_data.get('stream_url', '').strip()
        if audio_url.startswith('//'):
            audio_url = 'https:' + audio_url
        elif audio_url.startswith('http://'):
            audio_url = 'https://' + audio_url[len('http://'):]
        return audio_url if audio_url else None
    except Exception as e:
        logging.error(f"Lỗi khi xử lý flashData từ {detail_url}: {e}")
        return None

def register_nct(bot):
    # /nct command
    @bot.message_handler(commands=['nct'])
    def nhaccuatui(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, '🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /nct Tên bài hát', parse_mode='HTML')
            return
        keyword = args[1].strip()
        results = search_nhaccuatui(keyword)
        if not results:
            bot.reply_to(message, f'🚫 Không tìm thấy bài hát nào với từ khóa: {keyword}', parse_mode='HTML')
            return
        songs = results[:10]
        text = '<b>🎵 Kết quả tìm kiếm trên Nhaccuatui</b>\n\n'
        for i, song in enumerate(songs, 1):
            text += f"<b>{i}. {song['title']}</b>\n"
            text += f"👤 Nghệ sĩ: {song['artist']}\n"
            text += f"🆔 ID: {song['id']}\n\n"
        text += '<b>💡 Trả lời tin nhắn này bằng số từ 1-10 để chọn bài hát!</b>'
        sent = bot.reply_to(message, text, parse_mode='HTML')
        nct_data[sent.message_id] = {
            'user_id': message.from_user.id,
            'songs': songs
         }
    
    # Xử lý chọn bài
    @bot.message_handler(func=lambda m: m.reply_to_message and m.reply_to_message.message_id in nct_data)
    def handle_nct_selection(msg):
        reply_id = msg.reply_to_message.message_id
        if reply_id not in nct_data:
            return
        user_id = msg.from_user.id
    
        data = nct_data[reply_id]
        if user_id != data['user_id']:
            return
        text = msg.text.strip()
        if not text.isdigit():
            bot.reply_to(msg, '🚫 Vui lòng chỉ nhập số từ 1-10.', parse_mode='HTML')
            return
        idx = int(text) - 1
        if idx < 0 or idx >= len(data['songs']):
            bot.reply_to(msg, '🚫 Số không hợp lệ. Hãy nhập số từ 1-10.')
            return
        song = data['songs'][idx]
        bot.delete_message(msg.chat.id, reply_id)
        bot.reply_to(msg, f"🧭 Đang tải: {song['title']} - {song['artist']}")
        audio_url = get_download_url(song)
        if not audio_url:
            bot.reply_to(msg, '🚫 Không thể tải bài hát này.')
            return
        thumbnail_url = song.get("thumbnail")
        caption = f"""<blockquote>
    ⭔───────────────⭓
     <b>{song['title']}</b>
     Nghệ sĩ: {song['artist']}
     Nguồn: <b>NhacCuaTui</b> 
    ⭓───────────────⭔
    </blockquote>"""
        thumbnail_url = song.get("thumbnail")
        if thumbnail_url:
            try:
                bot.send_photo(msg.chat.id, thumbnail_url, caption=caption, parse_mode='HTML')
            except Exception:
                bot.reply_to(msg, caption + "\n🚫 Không thể tải thumbnail.", parse_mode='HTML')
        else:
            bot.reply_to(msg, caption, parse_mode='HTML')
        try:
            bot.send_audio(msg.chat.id, audio_url, title=song['title'], performer=song['artist'])
        except Exception:
            bot.reply_to(msg, '🚫 Không thể gửi audio.', parse_mode='HTML')
        del nct_data[reply_id]
