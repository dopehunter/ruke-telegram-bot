#!/bin/bash
echo "Upgrading pip..."
pip install --upgrade pip

echo "Uninstalling current python-telegram-bot to avoid conflicts..."
pip uninstall -y python-telegram-bot

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing alternative Telegram bot library..."
pip install pytelegrambotapi

echo "Dependencies installed. Ready to run the bot." 