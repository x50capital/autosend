#!/bin/bash

echo "🚀 Установка AutoSend..."

# 1. Обновление системы
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv tmux wget -y

# 2. Создание директории и установка окружения
mkdir -p ~/autosend && cd ~/autosend
python3 -m venv venv
source venv/bin/activate
pip install web3 eth-account

# 3. Скачивание файлов
wget -O autosend.py https://raw.githubusercontent.com/x50capital/autosend/main/autosend.py
wget -O config.json https://raw.githubusercontent.com/x50capital/autosend/main/config.json
wget -O wallets.json https://raw.githubusercontent.com/x50capital/autosend/main/wallets.json

# 4. Автозапуск через tmux
tmux new -d -s autosend "source venv/bin/activate && python autosend.py"

echo "✅ AutoSend установлен и запущен!"
echo "📌 Для проверки логов: tail -f ~/autosend/autosend.log"
