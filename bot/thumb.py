from io import BytesIO

user_thumb_state = {}

def register_thumb(bot):
    @bot.message_handler(commands=['thumb'])
    def ask_for_thumbnail(message):
        if not message.reply_to_message or not message.reply_to_message.document:
            return bot.reply_to(message, "⚠️ Hãy reply file bằng lệnh /thumb để thêm thumbnail.")
    
        sent = bot.reply_to(message, "📷 Gửi ảnh JPG làm thumbnail cho file.")
        
        # Lưu trạng thái của người dùng
        user_thumb_state[message.from_user.id] = {
            'file_id': message.reply_to_message.document.file_id,
            'file_name': message.reply_to_message.document.file_name,
            'ask_msg_id': sent.message_id,
            'thumb_cmd_msg_id': message.message_id  # Ghi nhớ lệnh /thumb
        }
    
    @bot.message_handler(content_types=['photo'])
    def handle_thumbnail(message):
        user_id = message.from_user.id
        if user_id not in user_thumb_state:
            return
    
        state = user_thumb_state.pop(user_id)
        try:
            # Tải dữ liệu
            doc_info = bot.get_file(state['file_id'])
            doc_data = bot.download_file(doc_info.file_path)
    
            thumb_info = bot.get_file(message.photo[-1].file_id)
            thumb_data = bot.download_file(thumb_info.file_path)
    
            doc_stream = BytesIO(doc_data)
            thumb_stream = BytesIO(thumb_data)
            doc_stream.name = state.get("file_name", "file")
            thumb_stream.name = "thumb.jpg"
    
            # Gửi lại file dưới dạng reply của /thumb
            bot.send_document(
                chat_id=message.chat.id,
                document=doc_stream,
                thumb=thumb_stream,
                caption="File đã được thêm thumbnail.",
                reply_to_message_id=state['thumb_cmd_msg_id']
            )
    
        except Exception:
            bot.reply_to(message, "❌ Đã xảy ra lỗi khi xử lý thumbnail.")

        # Xoá ảnh + yêu cầu ảnh
        try:
            bot.delete_message(message.chat.id, message.message_id)  # Ảnh
            bot.delete_message(message.chat.id, state['ask_msg_id'])  # Tin nhắn yêu cầu ảnh
        except:
            pass