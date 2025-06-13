import requests
from concurrent.futures import ThreadPoolExecutor

# 🔗 Nguồn proxy theo loại
PROXY_SOURCES = {
    "http": [
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
    ],
    "socks5": [
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
    ],
    "socks4": [
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


def fetch_proxies(url: str) -> list[str]:
    try:
        r = requests.get(url, timeout=10)
        if r.ok:
            return r.text.splitlines()
    except requests.RequestException:
        pass
    return []


def check_proxy(proxy: str, ptype: str = "http", timeout: int = 5) -> str | None:
    proxies = {scheme: f"{ptype}://{proxy}" for scheme in ("http", "https")}
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout, stream=True)
        if r.ok:
            return proxy
    except requests.RequestException:
        return None


def update_proxies() -> int:
    all_proxies = set()

    for ptype, urls in PROXY_SOURCES.items():
        raw = set()
        for url in urls:
            raw.update(fetch_proxies(url))

        with ThreadPoolExecutor(max_workers=50) as pool:
            futures = [pool.submit(check_proxy, proxy, ptype) for proxy in raw]
            alive = [f.result() for f in futures if f.result()]

        with open(f"{ptype}.txt", "w") as f:
            f.write("\n".join(alive))
        all_proxies.update(alive)

    with open("PROXY_FREE.txt", "w") as f:
        f.write("\n".join(all_proxies))
    return len(all_proxies)


def register_proxy(bot):
    @bot.message_handler(commands=["proxy"])
    def send_proxy(msg):
        bot.send_chat_action(msg.chat.id, "upload_document")
        total = update_proxies()
        with open("PROXY_FREE.txt", "rb") as f:
            bot.send_document(
                chat_id=msg.chat.id,
                document=f,
                caption=f"🚀 *FREE PROXY* 🚀\n📌 *Total:* {total} proxies",
                parse_mode="Markdown",
                reply_to_message_id=msg.message_id
            )
