import requests

def register_github(bot):
    @bot.message_handler(commands=['github']) 
    def handle_infogithub(message): 
        try: 
            username = message.text.split()[1]  
            api_url = f"https://api.github.com/users/{username}" 
            response = requests.get(api_url) 
            data = response.json() 
     
            if response.status_code == 200:
                avatar_url = data.get('avatar_url', 'Không có avatar')
                caption = f"""<blockquote>
⭔───────────────⭓
   <b>INFO GITHUB</b>
» <b>user:</b> {data.get('login', 'Không có')}
» <b>ID:</b> {data.get('id', 'Không có')}
» <b>Tên:</b> {data.get('name', 'Không có')} 
» <b>Bio:</b> {data.get('bio', 'Không có')}
» <b>Số repositories:</b> {data.get('public_repos', 0)} 
» <b>Số người theo dõi:</b> {data.get('followers', 0)} 
» <b>Số người đang theo dõi:</b> {data.get('following', 0)} 
» <b>Ngày tạo tài khoản:</b> {data.get('created_at', 'Không có')} 
» <b>Link:</b> {data.get('html_url', 'Không có')}
⭓───────────────⭔
</blockquote>"""
     
                bot.send_photo(message.chat.id, avatar_url, caption=caption, parse_mode='HTML') 
            else: 
                bot.reply_to(message, "Không tìm thấy thông tin Github của người dùng. Vui lòng thử lại.") 
     
        except IndexError: 
            bot.reply_to(message, "Vui lòng cung cấp username sau lệnh /github. Ví dụ: /github HgAnh7")
