
def register_document(bot):

    user_sessions = {}
    
    @bot.message_handler(commands=['sendfile'])
    def handle_send(message):
        user_id = message.from_user.id
        user_sessions[user_id] = {"state": "waiting", "thumb": None, "file": None}
        bot.reply_to(message, "📥 Gửi ảnh thumbnail và file bất kỳ (ảnh trước, file sau).")
    
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        user_id = message.from_user.id
        session = user_sessions.get(user_id)
    
        if session and session["state"] == "waiting":
            file_id = message.photo[-1].file_id
            session["thumb"] = file_id
            check_and_send(message, session)
    
    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        user_id = message.from_user.id
        session = user_sessions.get(user_id)
    
        if session and session["state"] == "waiting":
            file_id = message.document.file_id
            file_name = message.document.file_name
            session["file"] = {"file_id": file_id, "file_name": file_name}
            check_and_send(message, session)
    
    def check_and_send(message, session):
        user_id = message.from_user.id
        if session["thumb"] and session["file"]:
            # Tải thumbnail
            thumb_info = bot.get_file(session["thumb"])
            thumb_data = bot.download_file(thumb_info.file_path)
    
            # Tải file document
            doc_info = bot.get_file(session["file"]["file_id"])
            doc_data = bot.download_file(doc_info.file_path)
    
            # Gửi lại file kèm thumbnail
            bot.send_document(
                message.chat.id,
                document=doc_data,
                thumb=thumb_data,
                visible_file_name=session["file"]["file_name"]
            )
    
            bot.send_message(message.chat.id, "✅ Đã gửi lại file kèm thumbnail.")
    
            # Reset session
            user_sessions.pop(user_id, None)
    