@echo off
chcp 65001 >nul
title Bot Telegram - Chạy nhanh
color 0A

echo ===============================================
echo           BOT TELEGRAM - CHẠY NHANH  
echo ===============================================
echo.

REM Kiểm tra file .env
if not exist .env (
    echo ❌ File .env không tồn tại!
    echo 📝 Vui lòng chạy setup_and_run.bat trước
    pause
    exit /b 1
)

REM Kiểm tra token
findstr /C:"your_telegram_bot_token_here" .env >nul
if not errorlevel 1 (
    echo ❌ Token bot chưa được thiết lập!
    echo 🔑 Vui lòng chỉnh sửa file .env với token thật
    pause
    notepad .env
    exit /b 1
)

echo 🤖 Đang khởi động bot...
echo 📱 Kiểm tra bot trên Telegram
echo 🛑 Nhấn Ctrl+C để dừng
echo.

python main.py

echo.
echo 🛑 Bot đã dừng
pause
