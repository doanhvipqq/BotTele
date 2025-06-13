import requests

# 📦 Danh sách nguồn proxy theo loại
PROXY_SOURCES = {
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
            "https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt"
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
    }
}


# 🔌 Lấy proxy từ 1 URL
def fetch_proxies(url):
    try:
        r = requests.get(url, timeout=10)
        if r.ok:
            return set(r.text.strip().splitlines())
    except:
        return set()
    return set()


# 🧹 Tải proxy theo từng loại và lưu
def update_proxies():
    all_proxies = set()

    for proxy_type, info in PROXY_SOURCES.items():
        proxies = set()
        for url in info["urls"]:
            proxies |= fetch_proxies(url)

        with open(info["filename"], "w") as f:
            f.write("\n".join(sorted(proxies)))

        all_proxies |= proxies

    with open("PROXY_FREE.txt", "w") as f:
        f.write("\n".join(sorted(all_proxies)))

    return len(all_proxies)


# 🤖 Đăng ký lệnh proxy cho bot
def register_proxy(bot):
    @bot.message_handler(commands=["proxy"])
    def send_proxy(msg):
        bot.send_chat_action(msg.chat.id, "upload_document")
        total = update_proxies()
        with open("PROXY_FREE.txt", "rb") as f:
            bot.send_document(
                msg.chat.id, f,
                caption = f"📌 <b>Tổng cộng:</b> {total} proxies",
                parse_mode="HTML",
                reply_to_message_id=msg.message_id
            )
