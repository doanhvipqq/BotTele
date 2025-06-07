https://www.tikwm.com/api/?url=https%3A%2F%2Fwww.tiktok.com%2F%40hganh_7%2Fvideo%2F7453811758151617799
import requests

API_URL = "https://www.tikwm.com/api/"

def register_tiktok(bot):
    @bot.message_handler(commands=['tiktok'])
    def tiktok_info(message):
        try:
            args = message.text.split(" ", 1)
            if len(args) < 2:
                bot.reply_to(message, "🚫 Vui lòng gửi link TikTok sau lệnh /tiktok")
                return

            url = args[1]
            params = {'url': url}
            response = requests.get(API_URL, params=params).json()

            if response.get("code") != 0:
                bot.reply_to(message, "🚫 Không thể lấy dữ liệu. Vui lòng thử lại!")
                return

            data = response["data"]
            author_info = data.get("author", {})

            # Lấy thông tin từ API
            video_url = data.get("play")
            music_url = data.get("music", "Không có")
            title = data.get("title", "Không có tiêu đề")
            author = author_info.get("nickname", "Không rõ")
            avatar = author_info.get("avatar", "")
            region = data.get("region", "Không xác định")
            duration = data.get("duration", 0)
            likes = data.get("digg_count", 0)
            comments = data.get("comment_count", 0)
            shares = data.get("share_count", 0)
            views = data.get("play_count", 0)
            verified = "Đã xác minh" if author_info.get("verified", False) else "Chưa xác minh"
            unique_id = author_info.get("unique_id", "Không có ID")
            sec_uid = author_info.get("sec_uid", "Không có UID bảo mật")
            following_count = author_info.get("following_count", 0)
            video_count = author_info.get("video_count", 0)
            share_url = data.get("share_url", "Không có link chia sẻ")

            info_text = f"""<blockquote>⭔───────────────⭓
    <b>{title}</b>
    » <b>Khu vực:</b> {region}
    » <b>Thời lượng:</b> {duration} giây
    » <b>Lượt thích:</b> {likes}
    » <b>Bình luận:</b> {comments}
    » <b>Chia sẻ:</b> {shares}
    » <b>Lượt xem:</b> {views}
    » <b>Trạng thái tài khoản:</b> {verified}
    » <b>ID TikTok:</b> {unique_id}
    » <b>UID bảo mật:</b> {sec_uid}
    » <b>Đang theo dõi:</b> {following_count}
    » <b>Tổng số video:</b> {video_count}
    » <b>Link chia sẻ:</b> {share_url}
    » <b>Nhạc nền:</b> {music_url}
    ⭓───────────────⭔</blockquote>"""
            
            bot.send_photo(message.chat.id, avatar, caption=f"Người đăng: {author}")
            bot.send_video(message.chat.id, video_url, caption=info_text, parse_mode='HTML')

        except Exception as e:
            bot.reply_to(message, f"⚠️ Lỗi: {e}")
