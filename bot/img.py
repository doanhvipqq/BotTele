import time
import random
import requests
from bs4 import BeautifulSoup
from telebot.types import InputFile

def get_all_image_urls():

	headers = {"User-Agent": "Mozilla/5.0"}
	base_url = "https://cosplaytele.com/category/byoru/"

	all_image_urls = []
	visited_albums = []

	try:
		response = requests.get(base_url, headers=headers, timeout=10)
		soup = BeautifulSoup(response.text, "html.parser")

		a_tags = soup.find_all("a", class_="page-number")
		if a_tags:
			last_page = a_tags[-2].text
			print(f"Tổng số trang: {last_page}")
		else:
			print("Không tìm thấy số trang.")
			return
		
	###############################
		for page in range(1, int(last_page) +1):
			print(f"Đang xử lý trang {page}...")
			url_page = f"{base_url}page/{page}/"

			response = requests.get(url_page, headers=headers, timeout=10)
			soup = BeautifulSoup(response.text, "html.parser")
		# print(url_page)
	####################################
		
			album_container = soup.find_all("a", href=True, class_="plain")

			for container in album_container:
				href = container.get("href", "")
				if href.startswith("https://") and href not in visited_albums:
					visited_albums.append(href)

			for album_url in visited_albums:
				print(f"  → Lấy ảnh từ album: {album_url}")
				try:
					response = requests.get(album_url, headers=headers, timeout=10)
					soup = BeautifulSoup(response.text, "html.parser")

					img_tags = soup.find_all("img", src=True, class_="attachment-full size-full", alt=True)		
					for img in img_tags:
						src = img.get("src", "")
						if src.startswith("https://"):
							all_image_urls.append(src)

				except Exception as err:
					print(f"    ⚠️ Lỗi album: {err}")

				time.sleep(0.1)

			time.sleep(0.5)

	except Exception as e:
		print(f"Lỗi tổng thể: {e}")

	print(f"\nTổng số ảnh thu được: {len(all_image_urls)}")
	return all_image_urls
  
def register_img(bot):
  @bot.message_handler(commands=['img'])
  def handle_img(message):
  	msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")
  
  	image_urls = get_all_image_urls()
  
  	try:
  		if not image_urls:
  			bot.send_message(message.chat.id, "❌ Không tìm thấy ảnh nào.")
  			return
  
  		# Ghi vào file
  		with open("cosplay_links.txt", "w") as f:
  			f.write("\n".join(image_urls))
  
  		# Gửi file
  		bot.send_document(message.chat.id, InputFile("cosplay_links.txt"), caption=f"📦 Tổng cộng: {len(image_urls)} ảnh")
  	finally:
  		bot.delete_message(msg.chat.id, msg.message_id)
