import re
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

base_urls = [
    "https://viet69.fo/?s={}",
    "https://xnhau.dog/search/{}",
    "https://sexnhathd.blog/search/{}",
    "https://sexhihi.blog/search/{}",
    "https://lenlut.blog/search/{}"
]

def timkiem(search_term, max_pages=2, proxy_file=""):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
    }

    proxies_list = []
    if proxy_file:
        try:
            with open(proxy_file, 'r') as f:
                proxies_list = [line.strip() for line in f if line.strip()]
        except:
            print(f"Error reading {proxy_file}, running without proxies...")

    all_results = []

    for base_url in base_urls:
        for page in range(1, max_pages + 1):
            search_url = base_url.format(quote(search_term))
            if page > 1:
                search_url += f"&page={page}"

            try:
                if proxies_list:
                    proxy_ip_port = random.choice(proxies_list)
                    proxies = {
                        'http': f'http://{proxy_ip_port}',
                        'https': f'http://{proxy_ip_port}'
                    }
                else:
                    proxies = None

                response = requests.get(search_url, headers=headers, proxies=proxies, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                video_elements = soup.find_all('a', href=re.compile(r'https?://.*\d+.*'))

                for video in video_elements:
                    video_url = video.get('href')
                    title = video.find('h2') or video.find('h3') or video.get('title', 'No title')
                    if isinstance(title, str):
                        title_text = title
                    else:
                        title_text = title.text.strip() if title else 'No title'

                    if title_text == 'No title':
                        continue
                    if 'author/admin' in video_url or 'category' in video_url or 'tag' in video_url:
                        continue
                    if not ('video' in video_url.lower() or 'play' in video_url.lower() or 'stream' in video_url.lower() or re.search(r'\d{3,}', video_url)):
                        continue

                    all_results.append({
                        'site': base_url.format(''),
                        'title': title_text,
                        'url': video_url,
                        'page': page
                    })

            except:
                continue

    return all_results

def register_search(bot):
    @bot.message_handler(commands=['search'])
    def handle_search_command(message):
        args = message.text.split(' ', 1)
        if len(args) < 2 or not args[1].strip():
            bot.reply_to(message, "❗ Vui lòng nhập từ khoá sau lệnh:\nVí dụ: `/search em gai xinh`", parse_mode="Markdown")
            return
    
        search_term = args[1].strip()
        bot.send_chat_action(message.chat.id, 'typing')
        results = timkiem(search_term)
    
        if not results:
            bot.reply_to(message, "❌ Không tìm thấy kết quả.")
            return
    
        reply_text = ""
        for idx, res in enumerate(results[:10], 1):  # giới hạn 10 kết quả
            reply_text += f"{idx}. 📺 *{res['title']}*\n🔗 {res['url']}\n🌐 {res['site']}\n\n"
    
        bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)