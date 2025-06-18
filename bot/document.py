import os
from io import BytesIO

user_thumb_state = {}

def register_thumb(bot):
    @bot.message_handler(commands=['thumb'])
    def ask_for_thumbnail(message):
        if not message.reply_to_message or not message.reply_to_message.document:
            return bot.reply_to(message, "⚠️ Hãy dùng /thumb để trả lời một tin nhắn có chứa file.")
    
        user_thumb_state[message.from_user.id] = {
            'file_id': message.reply_to_message.document.file_id,
            'file_name': message.reply_to_message.document.file_name
        }
        bot.reply_to(message, "📷 Gửi ảnh JPG làm thumbnail cho file (ảnh dưới 200KB, 320x320px).")
    
    @bot.message_handler(content_types=['photo'])
    def handle_thumbnail(message):
        user_id = message.from_user.id
        if user_id not in user_thumb_state:
            return
    
        state = user_thumb_state.pop(user_id)
        try:
            # Tải file gốc và ảnh thumbnail
            doc_info = bot.get_file(state['file_id'])
            doc_data = bot.download_file(doc_info.file_path)
    
            photo = message.photo[-1]
            thumb_info = bot.get_file(photo.file_id)
            thumb_data = bot.download_file(thumb_info.file_path)
    
            # Dùng BytesIO thay vì file tạm
            doc_stream = BytesIO(doc_data)
            thumb_stream = BytesIO(thumb_data)
    
            doc_stream.name = state.get("file_name", "file")
            thumb_stream.name = "thumb.jpg"
    
            bot.send_document(
                chat_id=message.chat.id,
                document=doc_stream,
                thumb=thumb_stream,
                caption="✅ File đã được thêm thumbnail."
            )
    
            # Xoá ảnh
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi: {e}")