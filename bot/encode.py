import os
import subprocess

# Lưu chế độ encode của từng user: {user_id: mode}
user_modes = {}

def register_encode(bot):
	@bot.message_handler(commands=['encode'])
	def encode_command(message):
		# Lấy chế độ encode
		try:
			mode = message.text.split()[1]
			if mode not in ['1', '2']:
				bot.reply_to(message, "Chọn chế độ 1 hoặc 2!")
				return
			# Lưu chế độ và chờ file
			user_modes[message.from_user.id] = mode
			bot.reply_to(message, "Gửi file để encode!")
		except:
			bot.reply_to(message, "Dùng: /encode 1 hoặc 2")
	
	@bot.message_handler(content_types=['document'])
	def handle_file(message):
		user_id = message.from_user.id
		if user_id not in user_modes:
			return
	
		mode = user_modes.pop(user_id)  # Lấy và xóa mode sau khi dùng
		if not message.document.file_name.endswith(".py"):
			bot.reply_to(message, "Chỉ nhận file Python (.py)!")
			return
			
		try:
			# Tải file
			file_info = bot.get_file(message.document.file_id)
			file_name = message.document.file_name
			downloaded_file = bot.download_file(file_info.file_path)
			
			# Lưu file tạm
			input_file = f"./bot/encode/temp_{file_name}"
			with open(input_file, 'wb') as f:
				f.write(downloaded_file)
			
			# Gọi encode.py
			output_file = f"obf-{file_name}"
			subprocess.run(
				['python3', './bot/encode/Sakura.py', "-f", input_file", '-o', output_file, "-m", mode],
				check=True
			)
			
			# Gửi file encode
			with open(output_file, 'rb') as f:
				bot.send_document(message.chat.id, f, caption=f"File đã encode với chế độ {mode}!", visible_file_name=output_file)
	
			# Xóa file tạm
			os.remove(input_file)
			os.remove(output_file)
			
		except Exception as e:
			bot.reply_to(message, f"Lỗi: {str(e)}")
