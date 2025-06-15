import requests
from bs4 import BeautifulSoup
from telebot.types import Message

def register_search(bot):
    @bot.message_handler(commands=['search'])
    def search_command(message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "❌ Vui lòng nhập từ khóa.\nVí dụ: /search cách làm bánh mì")
            return

        query = args[1]
        bot.reply_to(message, f"🔎 Đang tìm kiếm: {query} ...")

        try:
            results = search_duckduckgo(query)
            if not results:
                bot.send_message(message.chat.id, "❌ Không tìm thấy kết quả.")
                return

            reply = f"📄 Kết quả cho: <b>{query}</b>\n\n"
            for i, item in enumerate(results, 1):
                reply += f"{i}. <a href=\"{item['href']}\">{item['title']}</a>\n"

            bot.send_message(message.chat.id, reply, parse_mode="HTML", disable_web_page_preview=True)

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Lỗi khi tìm kiếm: {e}")

def search_duckduckgo(query, limit=5):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    response = requests.get(url, headers=headers, timeout=10)

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    for a in soup.select('.result__a', limit=limit):
        href = a.get('href')
        title = a.get_text(strip=True)
        if href and title:
            results.append({'title': title, 'href': href})
    
    return results
