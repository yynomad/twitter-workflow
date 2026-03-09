"""
Telegram 消息推送模块
使用 Telegram Bot API 发送消息
"""

import requests
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TweetMessage:
    """推文消息"""
    tweet_text: str
    tweet_url: str
    author: str
    reply_options: List[dict]  # [{"style": "xx", "content": "xx"}]


class TelegramBot:
    """Telegram 机器人"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        初始化 Telegram 机器人
        
        Args:
            bot_token: Telegram Bot Token
            chat_id: 接收消息的聊天 ID（可以是用户 ID 或群组 ID）
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        发送文本消息
        
        Args:
            text: 消息内容（支持 HTML 格式）
            parse_mode: 解析模式，HTML 或 Markdown
            
        Returns:
            是否发送成功
        """
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True  # 不显示链接预览，节省空间
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if not result.get("ok", False):
            print(f"发送消息失败：{result.get('description', '未知错误')}")
            return False
        return True
    
    def send_tweet_with_replies(self, tweet_msg: TweetMessage) -> bool:
        """
        发送推文和回复选项
        
        消息格式：
        📌 新推文发现
        
        👤 @author
        📝 推文内容...
        
        🔗 https://twitter.com/...
        
        💡 建议回复：
        
        1️⃣ [友好]
        回复内容...
        
        2️⃣ [专业]
        回复内容...
        
        3️⃣ [幽默]
        回复内容...
        
        ─────────────
        操作：点击链接 → 复制回复 → 粘贴到评论区
        
        Args:
            tweet_msg: 推文消息对象
            
        Returns:
            是否发送成功
        """
        # 构建消息内容
        # 截断推文内容（如果太长）
        tweet_text = tweet_msg.tweet_text
        if len(tweet_text) > 200:
            tweet_text = tweet_text[:200] + "..."
        
        # 构建回复选项文本
        replies_text = ""
        for i, reply in enumerate(tweet_msg.reply_options, 1):
            emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i-1] if i <= 5 else f"{i}️⃣"
            style = reply.get("style", "通用")
            content = reply.get("content", "")
            replies_text += f"{emoji} <b>[{style}]</b>\n{content}\n\n"
        
        # 完整消息
        message = f"""📌 <b>新推文发现</b>

👤 @{tweet_msg.author}
📝 {tweet_text}

🔗 <a href="{tweet_msg.tweet_url}">打开推文</a>

💡 <b>建议回复：</b>

{replies_text}─────────────
<i>操作：点击上方链接 → 选择一条回复复制 → 粘贴到评论区</i>

<a href="{tweet_msg.tweet_url}">🚀 快速跳转到推文</a>"""
        
        return self.send_message(message)
    
    def send_batch(
        self,
        messages: List[TweetMessage],
        delay_between: int = 2
    ) -> int:
        """
        批量发送消息
        
        Args:
            messages: 消息列表
            delay_between: 消息间延迟（秒）
            
        Returns:
            成功发送的消息数量
        """
        import time
        success_count = 0
        
        for msg in messages:
            if self.send_tweet_with_replies(msg):
                success_count += 1
            if delay_between > 0:
                time.sleep(delay_between)
        
        return success_count
    
    def get_me(self) -> Optional[dict]:
        """获取机器人信息"""
        url = f"{self.base_url}/getMe"
        response = requests.get(url)
        result = response.json()
        return result.get("result") if result.get("ok") else None


def get_chat_id_from_updates(bot_token: str) -> List[dict]:
    """
    从更新记录中获取聊天 ID
    
    使用方法：
    1. 先给你的机器人发送一条消息
    2. 调用此函数获取聊天 ID
    3. 将获取的 ID 填入配置
    
    Args:
        bot_token: Bot Token
        
    Returns:
        聊天信息列表
    """
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    result = response.json()
    
    if not result.get("ok"):
        return []
    
    chats = []
    for update in result.get("result", []):
        message = update.get("message")
        if message:
            chat = message.get("chat", {})
            chats.append({
                "chat_id": chat.get("id"),
                "type": chat.get("type"),
                "username": chat.get("username"),
                "first_name": chat.get("first_name")
            })
    
    return chats
