import os
import requests
from concurrent.futures import ThreadPoolExecutor

# 📦 Nguồn proxy theo loại
proxy_sources = {
    "http": {
        "filename": "http.txt",
        "urls": [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/http.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt",
            "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
            "https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt",
        ]
    },
    "socks5": {
        "filename": "socks5.txt",
        "urls": [
            "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/BreakingTechFr/Proxy_Free/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/socks5.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt",
            "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
            "https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
        ]
    },
    "socks4": {
        "filename": "socks4.txt",
        "urls": [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/socks4.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt",
            "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
            "https://sunny9577.github.io/proxy-scraper/generated/socks4_proxies.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"
        ]
    }
}


# 🧠 Lấy proxy từ URL
def fetch_proxies(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.splitlines()
    except:
        pass
    return []


# ✅ Kiểm tra proxy có hoạt động không
def check_proxy(proxy, proxy_type="http", timeout=5):
    proxies = {
        "http": f"{proxy_type}://{proxy}",
        "https": f"{proxy_type}://{proxy}"
    }
    try:
        res = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
        if res.status_code == 200:
            return proxy
    except:
        return None

# 🔄 Tổng hợp proxy và lưu vào file
def update_proxies():
    all_proxies = []

    for proxy_type, source in proxy_sources.items():
        raw_proxies = []
        for url in source["urls"]:
            raw_proxies += fetch_proxies(url)

        raw_proxies = list(set(raw_proxies))  # ❗Sửa lại biến đúng

        # 🔍 Lọc proxy sống bằng đa luồng
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(check_proxy, p, proxy_type) for p in raw_proxies]
            filtered = [f.result() for f in futures if f.result()]

        # 📁 Ghi vào file riêng
        with open(source["filename"], "w") as f:
            f.write("\n".join(filtered))
        all_proxies += filtered

    # 📦 Ghi file tổng
    all_proxies = list(set(all_proxies))
    with open("PROXY_FREE.txt", "w") as f:
        f.write("\n".join(all_proxies))

    return len(all_proxies)

def register_proxy(bot):
    # 💬 Lệnh /proxy
    @bot.message_handler(commands=["proxy"])
    def send_proxy(msg):
        bot.send_chat_action(msg.chat.id, "upload_document")
        total = update_proxies()

        with open("PROXY_FREE.txt", "rb") as f:
            bot.send_document(
                chat_id=msg.chat.id,
                document=f,
                caption=f"🚀 *FREE PROXY* 🚀\n📌 *Total:* {total} proxies\n\n",
                parse_mode="Markdown",
                reply_to_message_id=msg.message_id  # 👈 Gửi dạng reply
            )
