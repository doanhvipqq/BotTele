import os
import zipfile
import tempfile
from PIL import Image


@bot.message_handler(content_types=['document'])
def convert_zip_to_pdfs(message):
    if not message.document.file_name.lower().endswith(".zip"):
        return bot.reply_to(message, "❗ Vui lòng gửi file .zip chứa ảnh trong các thư mục!")

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
    except Exception:
        return bot.reply_to(message, "❌ Không thể tải file từ Telegram.")

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "input.zip")
        with open(zip_path, "wb") as f:
            f.write(downloaded)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            return bot.reply_to(message, "❌ File không phải định dạng .zip hợp lệ.")

        sent = False
        for name in sorted(os.listdir(temp_dir)):
            folder = os.path.join(temp_dir, name)
            if not os.path.isdir(folder):
                continue

            images = sorted(
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            )

            if not images:
                continue

            try:
                pdf_path = os.path.join(temp_dir, f"{name}.pdf")
                imgs = [Image.open(p).convert("RGB") for p in images]
                imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:])

                with open(pdf_path, "rb") as pdf_file:
                    bot.send_document(message.chat.id, pdf_file, caption=f"📖 {name}")
                    sent = True
            except Exception:
                bot.reply_to(message, f"⚠️ Lỗi tạo PDF chương: {name}")

        if not sent:
            bot.reply_to(message, "❌ Không tìm thấy ảnh hợp lệ để tạo PDF.")
