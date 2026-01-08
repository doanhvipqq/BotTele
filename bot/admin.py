import re
from datetime import datetime, timedelta
from telebot import types

# ID Admin có quyền sử dụng lệnh
ADMIN_ID = 7509896689

def parse_duration(duration_str):
    """
    Phân tích chuỗi thời gian thành giây.
    Ví dụ: "5m" = 5 phút, "2h" = 2 giờ, "1d" = 1 ngày
    Hỗ trợ: s (giây), m (phút), h (giờ), d (ngày), y (năm)
    """
    match = re.match(r'^(\d+)([smhdy])$', duration_str.lower())
    if not match:
        return None
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    units = {
        's': 1,           # giây
        'm': 60,          # phút
        'h': 3600,        # giờ
        'd': 86400,       # ngày
        'y': 31536000     # năm (365 ngày)
    }
    
    return amount * units.get(unit, 0)


def register_admin(bot):
    @bot.message_handler(commands=['kick'])
    def kick_member(message):
        # Kiểm tra có phải admin không
        if message.from_user.id != ADMIN_ID:
            return bot.reply_to(message, "❌ Bạn không có quyền sử dụng lệnh này!")
        
        # Kiểm tra có phải trong group không
        if message.chat.type not in ['group', 'supergroup']:
            return bot.reply_to(message, "⚠️ Lệnh này chỉ dùng trong nhóm!")
        
        # Kiểm tra có reply user không
        if not message.reply_to_message:
            return bot.reply_to(message, "⚠️ Reply tin nhắn của người cần kick!")
        
        target_user = message.reply_to_message.from_user
        
        try:
            # Ban vĩnh viễn - KHÔNG cho vào lại nhóm
            bot.ban_chat_member(message.chat.id, target_user.id)
            
            bot.reply_to(
                message, 
                f"🚫 Đã kick và cấm <b>{target_user.first_name}</b> vĩnh viễn!\n"
                f"❌ User không thể vào lại nhóm.\n\n"
                f"<i>💡 Dùng /unban để bỏ cấm</i>",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {e}")

    
    
    @bot.message_handler(commands=['ban', 'mute'])
    def ban_member(message):
        # Kiểm tra có phải admin không
        if message.from_user.id != ADMIN_ID:
            return bot.reply_to(message, "❌ Bạn không có quyền sử dụng lệnh này!")
        
        # Kiểm tra có phải trong group không
        if message.chat.type not in ['group', 'supergroup']:
            return bot.reply_to(message, "⚠️ Lệnh này chỉ dùng trong nhóm!")
        
        # Kiểm tra có reply user không
        if not message.reply_to_message:
            return bot.reply_to(message, "⚠️ Reply tin nhắn của người cần cấm chat!\n\nVí dụ: /ban 5m (cấm 5 phút)\n/ban 1h (cấm 1 giờ)\n/ban 1d (cấm 1 ngày)")
        
        # Lấy thời gian từ lệnh
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return bot.reply_to(
                message, 
                "⚠️ Nhập thời gian cấm!\n\n"
                "Ví dụ:\n"
                "• /ban 30s (30 giây)\n"
                "• /ban 5m (5 phút)\n"
                "• /ban 2h (2 giờ)\n"
                "• /ban 1d (1 ngày)\n"
                "• /ban 1y (1 năm)"
            )
        
        duration_str = args[1].strip()
        duration_seconds = parse_duration(duration_str)
        
        if duration_seconds is None:
            return bot.reply_to(
                message, 
                "❌ Sai định dạng thời gian!\n\n"
                "Dùng: s (giây), m (phút), h (giờ), d (ngày), y (năm)\n"
                "Ví dụ: 5m, 2h, 1d"
            )
        
        target_user = message.reply_to_message.from_user
        
        try:
            # Tính thời điểm unban
            until_date = datetime.now() + timedelta(seconds=duration_seconds)
            
            # Cấm chat (restrict permissions)
            bot.restrict_chat_member(
                message.chat.id,
                target_user.id,
                until_date=until_date,
                permissions=types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            
            # Chuyển đổi thời gian sang text dễ đọc
            time_text = ""
            if duration_str.endswith('s'):
                time_text = f"{duration_seconds} giây"
            elif duration_str.endswith('m'):
                time_text = f"{duration_seconds // 60} phút"
            elif duration_str.endswith('h'):
                time_text = f"{duration_seconds // 3600} giờ"
            elif duration_str.endswith('d'):
                time_text = f"{duration_seconds // 86400} ngày"
            elif duration_str.endswith('y'):
                time_text = f"{duration_seconds // 31536000} năm"
            
            bot.reply_to(
                message,
                f"🔇 Đã cấm chat <b>{target_user.first_name}</b>\n"
                f"⏱ Thời gian: <b>{time_text}</b>\n"
                f"⏰ Hết hạn: <code>{until_date.strftime('%Y-%m-%d %H:%M:%S')}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {e}")
    
    
    @bot.message_handler(commands=['unban', 'unmute'])
    def unban_member(message):
        # Kiểm tra có phải admin không
        if message.from_user.id != ADMIN_ID:
            return bot.reply_to(message, "❌ Bạn không có quyền sử dụng lệnh này!")
        
        # Kiểm tra có phải trong group không
        if message.chat.type not in ['group', 'supergroup']:
            return bot.reply_to(message, "⚠️ Lệnh này chỉ dùng trong nhóm!")
        
        # Kiểm tra có reply user không
        if not message.reply_to_message:
            return bot.reply_to(message, "⚠️ Reply tin nhắn của người cần bỏ cấm!")
        
        target_user = message.reply_to_message.from_user
        
        try:
            # Bỏ ban vĩnh viễn (cho phép vào lại nhóm)
            bot.unban_chat_member(message.chat.id, target_user.id)
            
            # Đồng thời cho phép chat lại (trường hợp bị mute)
            bot.restrict_chat_member(
                message.chat.id,
                target_user.id,
                permissions=types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
            )
            
            bot.reply_to(
                message,
                f"✅ Đã bỏ cấm cho <b>{target_user.first_name}</b>!\n"
                f"🔓 User có thể vào lại nhóm và chat bình thường.",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {e}")

