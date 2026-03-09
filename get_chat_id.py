#!/usr/bin/env python3
"""
获取 Telegram Chat ID 工具

使用方法：
1. 先给你的机器人发送一条消息
2. 运行此脚本
3. 获取聊天 ID
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

if not bot_token:
    print("❌ 错误：TELEGRAM_BOT_TOKEN 未设置")
    print("请先复制 .env.example 为 .env 并填入你的 Bot Token")
    exit(1)

url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
response = requests.get(url)
result = response.json()

if not result.get("ok"):
    print(f"❌ 请求失败：{result.get('description', '未知错误')}")
    exit(1)

updates = result.get("result", [])

if not updates:
    print("⚠️  没有找到更新记录")
    print("\n请先给你的机器人发送一条消息，然后再运行此脚本")
    print(f"机器人链接：https://t.me/{bot_token.split(':')[0].replace('bot', '')}")
    exit(1)

print("✅ 找到以下聊天：\n")

for update in updates:
    message = update.get("message")
    if message:
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type")
        name = chat.get("first_name", "") + " " + chat.get("last_name", "")
        username = chat.get("username", "")
        
        print(f"Chat ID: {chat_id}")
        print(f"类型：{chat_type}")
        print(f"名称：{name.strip()}")
        print(f"用户名：@{username}" if username else "用户名：无")
        print("-" * 40)

print("\n将 Chat ID 填入 .env 文件的 TELEGRAM_CHAT_ID 变量中")
