import os
import re
import random
import telebot
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# --- CẤU HÌNH ---
BASE_URL = 'https://www.nhaccuatui.com'
API_SEARCH = BASE_URL + '/tim-kiem/bai-hat'

# Lưu tạm dữ liệu cho mỗi lần tìm kiếm theo user_id
nct_data = {}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "fr-FR,fr;q=0.9",
    "es-ES,es;q=0.9",
    "de-DE,de;q=0.9",
    "zh-CN,zh;q=0.9",
]

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES),
        'Referer': BASE_URL,
    }

def search_nhaccuatui(keyword, limit=10):
    params = {'q': keyword, 'b': 'keyword', 'l': 'tat-ca', 's': 'default'}
    try:
        resp = requests.get(API_SEARCH, params=params, headers=get_headers())
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('ul.sn_search_returns_list_song li.sn_search_single_song')[:limit]
    tracks = []
    for item in items:
        title_elem = item.select_one('h3.title_song a')
        artist_elem = item.select_one('h4.singer_song')
        detail_href = title_elem.get('href') if title_elem else None
        if title_elem and detail_href:
            # Phần ID vẫn lưu trong dict (nếu cần cho xử lý nội bộ) nhưng không hiển thị.
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

def get_download_url(track):
    detail_url = track.get('detail_url')
    if not detail_url:
        return None
    # Khởi tạo thumbnail mặc định là None
    track['thumbnail'] = None
    try:
        resp = requests.get(detail_url, headers=get_headers())
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException:
        return None
    try:
        soup = BeautifulSoup(html, 'html.parser')
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image and og_image.has_attr('content'):
            thumb_url = og_image['content'].strip()
            if thumb_url.startswith('//'):
                thumb_url = 'https:' + thumb_url
            track['thumbnail'] = thumb_url
    except Exception:
        track['thumbnail'] = None

    xml_match = re.search(
        r"peConfig\.xmlURL\s*=\s*['\"](https://www\.nhaccuatui\.com/flash/xml\?html5=true&key1=[^'\"]+)['\"]",
        html
    )
    if not xml_match:
        return None
    xml_url = xml_match.group(1)
    try:
        xml_resp = requests.get(xml_url, headers={**get_headers(), 'Referer': detail_url})
        xml_resp.raise_for_status()
        xml_content = xml_resp.text
    except requests.exceptions.RequestException:
        return None
    try:
        root = ET.fromstring(xml_content)
        loc = root.find('.//location')
        if loc is not None and loc.text:
            audio_url = loc.text.strip()
            if audio_url.startswith('//'):
                audio_url = 'https:' + audio_url
            elif audio_url.startswith('http://'):
                audio_url = 'https://' + audio_url[len('http://'):]
            return audio_url
    except ET.ParseError:
        return None
    return None

def register_nct(bot):
    """
    Đăng ký handler cho lệnh /nct và xử lý lựa chọn bài hát bằng inline keyboard.
    """
    from telebot import types

    @bot.message_handler(commands=['nct'])
    def nhaccuatui(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(
                message,
                '🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /nct Tên bài hát',
                parse_mode='HTML'
            )
            return
        keyword = args[1].strip()
        results = search_nhaccuatui(keyword)
        if not results:
            bot.reply_to(
                message,
                f'🚫 Không tìm thấy bài hát nào với từ khóa: {keyword}',
                parse_mode='HTML'
            )
            return
        songs = results[:10]
        text = '<b>🎵 Kết quả tìm kiếm trên Nhaccuatui</b>\n\n'
        for i, song in enumerate(songs, 1):
            text += f"<b>{i}. {song['title']}</b>\n"
            text += f"👤 Nghệ sĩ: {song['artist']}\n\n"
        text += '<b>💡 Chọn bài hát bạn muốn tải:</b>'
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons = []
        for i in range(len(songs)):
            button = types.InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"nct_{message.from_user.id}_{i}"
            )
            buttons.append(button)
        markup.add(*buttons)
        sent = bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        nct_data[str(message.from_user.id)] = {
            'songs': songs,
            'message_id': sent.message_id
        }

    @bot.callback_query_handler(func=lambda call: call.data.startswith('nct_'))
    def handle_nct_callback(call):
        try:
            parts = call.data.split('_')
            user_id = int(parts[1])
            song_index = int(parts[2])
            if call.from_user.id != user_id:
                bot.answer_callback_query(call.id, "❌ Bạn không có quyền sử dụng nút này!", show_alert=True)
                return
            if str(user_id) not in nct_data:
                bot.answer_callback_query(call.id, "❌ Dữ liệu đã hết hạn!", show_alert=True)
                return
            data = nct_data[str(user_id)]
            songs = data['songs']
            if song_index < 0 or song_index >= len(songs):
                bot.answer_callback_query(call.id, "❌ Lựa chọn không hợp lệ!", show_alert=True)
                return
            song = songs[song_index]
            bot.answer_callback_query(call.id, f"🧭 Đang tải: {song['title']}")
            # Cập nhật thông báo loading (đang tải)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🧭 Đang tải: <b>{song['title']}</b>\n👤 Nghệ sĩ: {song['artist']}\n\n⏳ Vui lòng chờ...",
                parse_mode='HTML'
            )
            audio_url = get_download_url(song)
            if not audio_url:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="🚫 Không thể tải bài hát này.",
                    parse_mode='HTML'
                )
                return
            thumbnail_url = song.get('thumbnail')
            caption = f"""<blockquote>
⭔───────────────⭓
 <b>{song['title']}</b>
 Nghệ sĩ: {song['artist']}
 Nguồn: <b>NhacCuaTui</b> 
⭓───────────────⭓
</blockquote>"""
            if thumbnail_url:
                try:
                    bot.send_photo(call.message.chat.id, thumbnail_url, caption=caption, parse_mode='HTML')
                except Exception:
                    bot.send_message(call.message.chat.id, caption + "\n🚫 Không thể tải thumbnail.", parse_mode='HTML')
            else:
                bot.send_message(call.message.chat.id, caption, parse_mode='HTML')
            try:
                bot.send_audio(call.message.chat.id, audio_url, title=song['title'], performer=song['artist'])
            except Exception:
                bot.send_message(call.message.chat.id, '🚫 Không thể gửi audio.', parse_mode='HTML')
            # Xóa luôn thông báo loading khi tải nhạc hoàn tất
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            if str(user_id) in nct_data:
                del nct_data[str(user_id)]
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Có lỗi xảy ra: {str(e)}", show_alert=True)
