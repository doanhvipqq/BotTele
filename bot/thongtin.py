import telebot
from telebot.types import Message
from datetime import datetime

def register_thongtin(bot):
    @bot.message_handler(commands=['thongtin'])
    def handle_check(message: Message):
        try:
            # Lấy thông tin người dùng mục tiêu
            user = message.reply_to_message.from_user if message.reply_to_message else message.from_user

            # Lấy thông tin chi tiết qua các cuộc gọi API
            user_photos = bot.get_user_profile_photos(user.id)
            chat_info = bot.get_chat(user.id)
            bio = chat_info.bio or "Không có"
            
            user_first_name = user.first_name
            user_last_name = user.last_name or ""
            user_username = (f"@{user.username}") if user.username else "Không có"
            user_language = user.language_code or "Không xác định"

            # Mặc định trạng thái là "Không trong nhóm" nếu chat là private
            status = "Trong cuộc trò chuyện riêng"
            joined_date = "Không khả dụng"
            message_count = "Không thể lấy thông tin này trực tiếp từ API Telegram"

            if message.chat.type in ['group', 'supergroup']:
                status_dict = {
                    "creator": "👑 Quản trị viên cao nhất",
                    "administrator": "🛡️ Quản trị viên",
                    "member": "👤 Thành viên",
                    "restricted": "🚫 Bị hạn chế",
                    "left": "👋 Đã rời đi",
                    "kicked": "👢 Đã bị kick"
                }
                chat_member = bot.get_chat_member(message.chat.id, user.id)
                status = status_dict.get(chat_member.status, "Không xác định")
                
                # Lấy ngày tham gia nhóm
                if hasattr(chat_member, 'joined_date'):
                    joined_date = datetime.fromtimestamp(chat_member.joined_date).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    joined_date = "Không có thông tin"

            # Chuẩn bị nội dung tin nhắn
            caption = (
                f"👤 <b>Thông Tin Của {'Bạn' if user.id == message.from_user.id else 'Người Dùng'}</b>\n"
                f"<blockquote>┌ ID: <code>{user.id}</code>\n"
                f"├ Tên: {user_first_name} {user_last_name}\n"
                f"├ Username: {user_username}\n"
                f"├ Ngôn ngữ mặc định: {user_language}\n"
                f"├ Trạng thái trong nhóm: {status}\n"
                f"├ Ngày tham gia nhóm: {joined_date}\n"
                f"├ Số lượng tin nhắn đã gửi: {message_count}\n"
                f"├ Bio: {bio}\n"
                f"└ Avatar: {'✅ Có' if user_photos.total_count > 0 else '❌ Không'}</blockquote>"
            )

            # Gửi ảnh đại diện nếu có
            if user_photos.total_count > 0:
                avatar_file_id = user_photos.photos[0][-1].file_id
                bot.send_photo(message.chat.id, avatar_file_id, caption=caption, parse_mode='HTML', reply_to_message_id=message.message_id)
            else:
                bot.reply_to(message, caption, parse_mode='HTML')

        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            bot.reply_to(message, "😕 Rất tiếc, đã có lỗi xảy ra khi lấy thông tin. Người dùng có thể đã chặn bot hoặc bot không có đủ quyền.")
