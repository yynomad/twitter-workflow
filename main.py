#!/usr/bin/env python3
"""
Twitter 自动回复工作流 - 主脚本

功能：定时抓取推文 → AI 生成回复 → Telegram 推送 → 人工审核发布
"""

import os
import sys
import json
import asyncio
import argparse
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from twitter_scraper import TwitterScraper, Tweet
from reply_generator import ReplyGenerator
from telegram_bot import TelegramBot, TweetMessage


# ============== 配置管理 ==============

DEFAULT_CONFIG = {
    "search": {
        "query": "AI OR 人工智能",
        "time_range_hours": 24,
        "min_likes": 10
    },
    "selection": {
        "mode": "random",
        "count": 1
    },
    "rate_limit": {
        "enabled": True,
        "interval_minutes": 5
    },
    "reply": {
        "custom_instructions": "回复要友好、有建设性",
        "language": "中文",
        "styles": ["专业", "幽默", "友好"]
    }
}


def load_config(config_file: str = "config.json") -> dict:
    """加载配置文件"""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            for key, value in user_config.items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value
    
    # 环境变量覆盖
    if os.getenv("TWITTER_SEARCH_QUERY"):
        config["search"]["query"] = os.getenv("TWITTER_SEARCH_QUERY")
    if os.getenv("TWITTER_HOURS"):
        config["search"]["time_range_hours"] = int(os.getenv("TWITTER_HOURS"))
    if os.getenv("TWITTER_MIN_LIKES"):
        config["search"]["min_likes"] = int(os.getenv("TWITTER_MIN_LIKES"))
    
    return config


# ============== 频率限制 ==============

RATE_LIMIT_FILE = "rate_limit_state.json"


def load_rate_limit_state() -> dict:
    """加载频率限制状态"""
    if os.path.exists(RATE_LIMIT_FILE):
        with open(RATE_LIMIT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_run": None, "runs_today": 0, "last_reset_date": datetime.now().strftime("%Y-%m-%d")}


def save_rate_limit_state(state: dict):
    """保存频率限制状态"""
    with open(RATE_LIMIT_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_rate_limit(config: dict) -> tuple[bool, str]:
    """检查频率限制"""
    rate_config = config.get("rate_limit", {})
    
    if not rate_config.get("enabled", False):
        return True, "频率限制未启用"
    
    state = load_rate_limit_state()
    now = datetime.now()
    
    # 重置每日计数
    today = now.strftime("%Y-%m-%d")
    if state["last_reset_date"] != today:
        state["runs_today"] = 0
        state["last_reset_date"] = today
    
    # 检查间隔
    interval = rate_config.get("interval_minutes", 5)
    if state["last_run"]:
        last_run = datetime.fromisoformat(state["last_run"])
        elapsed = (now - last_run).total_seconds() / 60
        if elapsed < interval:
            wait_time = int(interval - elapsed)
            return False, f"需等待 {wait_time} 分钟"
    
    return True, "可以运行"


def update_rate_limit_state():
    """更新频率限制状态"""
    state = load_rate_limit_state()
    state["last_run"] = datetime.now().isoformat()
    state["runs_today"] += 1
    save_rate_limit_state(state)


# ============== 推文筛选 ==============

def filter_tweets_by_time(tweets: list[Tweet], hours: int) -> list[Tweet]:
    """筛选时间范围内的推文"""
    if hours <= 0:
        return tweets
    
    cutoff = datetime.now() - timedelta(hours=hours)
    filtered = []
    
    for tweet in tweets:
        try:
            if hasattr(tweet, 'created_at') and tweet.created_at:
                tweet_time = datetime.fromisoformat(tweet.created_at.replace('Z', '+00:00'))
                if tweet_time.tzinfo:
                    tweet_time = tweet_time.replace(tzinfo=None)
                if tweet_time >= cutoff:
                    filtered.append(tweet)
        except:
            continue
    
    return filtered


def select_tweets(tweets: list[Tweet], mode: str = "random", count: int = 1) -> list[Tweet]:
    """选择推文"""
    if not tweets:
        return []
    
    if mode == "random":
        return random.sample(tweets, min(count, len(tweets)))
    else:
        return tweets[:count]


# ============== 登录功能（集成） ==============

async def login_twitter():
    """登录 Twitter 并保存 Cookie"""
    scraper = TwitterScraper(headless=False)
    
    try:
        await scraper.start()
        print("\n📱 请在浏览器中登录 Twitter...")
        print("   登录后按回车键保存 Cookie\n")
        
        await scraper.page.goto("https://twitter.com/login", wait_until="domcontentloaded")
        
        try:
            await scraper.page.wait_for_url("https://twitter.com/home", timeout=120000)
            print("✅ 检测到登录成功")
        except:
            print("⚠️  等待登录超时")
        
        input("按回车键保存 Cookie...")
        await scraper.save_cookies()
        print("✅ Cookie 已保存")
        
    finally:
        await scraper.close()


# ============== 主工作流 ==============

async def run_workflow(config: dict, dry_run: bool = False, headless: bool = True):
    """执行工作流"""
    print(f"🚀 Twitter 工作流 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 频率检查
    print("\n⏰ 检查频率限制...")
    allowed, reason = check_rate_limit(config)
    if not allowed:
        print(f"   ⚠️  {reason}")
        return
    print(f"   ✅ {reason}")
    
    # 初始化
    print("\n📋 初始化组件...")
    
    volc_key = os.getenv("VOLC_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not volc_key or not telegram_token or not telegram_chat_id:
        print("❌ 错误：请检查 .env 配置")
        sys.exit(1)
    
    scraper = TwitterScraper(headless=headless)
    await scraper.start()
    
    if not await scraper.is_logged_in():
        print("❌ Twitter 未登录，请先运行：python main.py --login")
        await scraper.close()
        sys.exit(1)
    
    generator = ReplyGenerator(api_key=volc_key)
    bot = TelegramBot(telegram_token, telegram_chat_id)
    
    print("✅ 组件就绪")
    
    # 搜索推文
    search_cfg = config.get("search", {})
    print(f"\n🔍 搜索推文...")
    print(f"   查询：{search_cfg.get('query', '')}")
    print(f"   时间：{search_cfg.get('time_range_hours', 24)}h 内")
    print(f"   最小点赞：{search_cfg.get('min_likes', 0)}")
    
    tweets = await scraper.search_tweets(
        query=search_cfg.get("query", ""),
        max_results=50,
        min_likes=search_cfg.get("min_likes", 0)
    )
    print(f"   初始：{len(tweets)} 条")
    
    # 筛选
    tweets = filter_tweets_by_time(tweets, search_cfg.get("time_range_hours", 24))
    print(f"   时间筛选后：{len(tweets)} 条")
    
    if not tweets:
        print("✅ 无符合条件的推文")
        await scraper.close()
        return
    
    # 选择
    selection_cfg = config.get("selection", {})
    selected = select_tweets(
        tweets,
        mode=selection_cfg.get("mode", "random"),
        count=selection_cfg.get("count", 1)
    )
    print(f"   选中：{len(selected)} 条")
    
    # 生成回复并发送
    print(f"\n💡 生成回复...")
    reply_cfg = config.get("reply", {})
    
    for tweet in selected:
        print(f"\n   处理：@{tweet.author_username}")
        
        result = generator.generate_replies(
            tweet_text=tweet.text,
            tweet_author=tweet.author_username,
            num_replies=3,
            custom_instructions=reply_cfg.get("custom_instructions", ""),
            language=reply_cfg.get("language", "中文")
        )
        
        print(f"   ✅ 生成 {len(result['replies'])} 条回复")
        
        # 构建消息
        tweet_display = tweet.text
        if result.get('translated_tweet'):
            tweet_display = f"{tweet.text}\n\n[翻译]\n{result['translated_tweet']}"
        
        reply_options = []
        for r in result['replies']:
            reply_text = r['content']
            if r.get('translation'):
                reply_text = f"{r['content']}\n\n[翻译]\n{r['translation']}"
            reply_options.append({"style": r['style'], "content": reply_text})
        
        msg = TweetMessage(
            tweet_text=tweet_display,
            tweet_url=tweet.url,
            author=tweet.author_username,
            reply_options=reply_options
        )
        
        if not dry_run:
            bot.send_tweet_with_replies(msg)
            print("   📤 已发送到 Telegram")
        else:
            print(f"   🧪 测试模式：{msg.tweet_text[:50]}...")
    
    await scraper.close()
    update_rate_limit_state()
    
    print(f"\n✅ 完成！请查看 Telegram")


def run_workflow_sync(config: dict, dry_run: bool = False, headless: bool = True):
    """同步包装器"""
    asyncio.run(run_workflow(config, dry_run, headless))


def main():
    parser = argparse.ArgumentParser(description="Twitter 自动回复工作流")
    parser.add_argument("--login", action="store_true", help="登录 Twitter")
    parser.add_argument("--visible", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--dry-run", action="store_true", help="测试模式，不发送消息")
    parser.add_argument("--config", type=str, default="config.json", help="配置文件路径")
    
    args = parser.parse_args()
    
    if args.login:
        asyncio.run(login_twitter())
        return
    
    config = load_config(args.config)
    run_workflow_sync(config, dry_run=args.dry_run, headless=not args.visible)


if __name__ == "__main__":
    main()
