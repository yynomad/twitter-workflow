#!/usr/bin/env python3
"""
Twitter 自动回复工作流 - 主脚本（增强版）

新增功能：
- 时间范围筛选（h 小时内）
- 曝光量筛选（views > x）
- 随机返回模式
- 频率限制（每 m 分钟执行一次）
"""

import os
import sys
import json
import asyncio
import argparse
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from twitter_scraper import TwitterScraper, Tweet
from reply_generator import ReplyGenerator
from telegram_bot import TelegramBot, TweetMessage


# ============== 配置文件管理 ==============

DEFAULT_CONFIG = {
    "search": {
        "query": "AI OR 人工智能",
        "time_range_hours": 24,
        "min_likes": 10,
        "min_retweets": 0,
        "min_views": 1000,
        "exclude_replies": True,
        "exclude_retweets": True,
        "language": "en"
    },
    "selection": {
        "mode": "random",  # random, latest, top
        "count": 1,
        "sort_by": "engagement"  # engagement, likes, retweets, views
    },
    "rate_limit": {
        "enabled": True,
        "interval_minutes": 30,
        "max_per_hour": 10,
        "max_per_day": 50
    },
    "reply": {
        "custom_instructions": "回复要友好、有建设性",
        "language": "中文",
        "styles": ["专业", "幽默", "友好"]
    },
    "telegram": {
        "enabled": True,
        "batch_send": False
    }
}


def load_config(config_file: str = "config.json") -> dict:
    """加载配置文件，合并默认配置"""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            # 深度合并配置
            deep_merge(config, user_config)
    
    return config


def deep_merge(base: dict, override: dict):
    """深度合并两个字典"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value


def save_config(config: dict, config_file: str = "config.json"):
    """保存配置文件"""
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ============== 频率限制管理 ==============

RATE_LIMIT_FILE = "rate_limit_state.json"


def load_rate_limit_state() -> dict:
    """加载频率限制状态"""
    if os.path.exists(RATE_LIMIT_FILE):
        with open(RATE_LIMIT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_run": None,
        "runs_today": 0,
        "runs_this_hour": 0,
        "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
        "last_reset_hour": datetime.now().strftime("%Y-%m-%d %H")
    }


def save_rate_limit_state(state: dict):
    """保存频率限制状态"""
    with open(RATE_LIMIT_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_rate_limit(config: dict) -> tuple[bool, str]:
    """
    检查是否超过频率限制
    返回：(是否允许执行，原因)
    """
    rate_config = config.get("rate_limit", {})
    
    if not rate_config.get("enabled", False):
        return True, "频率限制未启用"
    
    state = load_rate_limit_state()
    now = datetime.now()
    
    # 检查日期重置
    today = now.strftime("%Y-%m-%d")
    if state["last_reset_date"] != today:
        state["runs_today"] = 0
        state["last_reset_date"] = today
    
    # 检查小时重置
    current_hour = now.strftime("%Y-%m-%d %H")
    if state["last_reset_hour"] != current_hour:
        state["runs_this_hour"] = 0
        state["last_reset_hour"] = current_hour
    
    # 检查间隔限制
    interval = rate_config.get("interval_minutes", 30)
    if state["last_run"]:
        last_run = datetime.fromisoformat(state["last_run"])
        elapsed = (now - last_run).total_seconds() / 60
        if elapsed < interval:
            wait_time = int(interval - elapsed)
            return False, f"距离上次运行仅 {int(elapsed)} 分钟，需等待 {wait_time} 分钟"
    
    # 检查每小时限制
    max_per_hour = rate_config.get("max_per_hour", 10)
    if state["runs_this_hour"] >= max_per_hour:
        return False, f"已达到每小时最大运行次数 ({max_per_hour})"
    
    # 检查每天限制
    max_per_day = rate_config.get("max_per_day", 50)
    if state["runs_today"] >= max_per_day:
        return False, f"已达到每天最大运行次数 ({max_per_day})"
    
    return True, "频率检查通过"


def update_rate_limit_state():
    """更新频率限制状态"""
    state = load_rate_limit_state()
    state["last_run"] = datetime.now().isoformat()
    state["runs_today"] += 1
    state["runs_this_hour"] += 1
    save_rate_limit_state(state)


# ============== 推文筛选 ==============

def filter_tweets_by_time(tweets: list[Tweet], hours: int) -> list[Tweet]:
    """筛选指定时间范围内的推文"""
    if hours <= 0:
        return tweets
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    filtered = []
    
    for tweet in tweets:
        # 尝试解析推文时间
        try:
            if hasattr(tweet, 'created_at') and tweet.created_at:
                tweet_time = parse_tweet_time(tweet.created_at)
                if tweet_time and tweet_time.tzinfo is not None:
                    tweet_time = tweet_time.replace(tzinfo=None)

                if tweet_time and tweet_time >= cutoff_time:
                    filtered.append(tweet)
        except Exception as e:
            # 无法解析时间的推文跳过
            continue
    
    return filtered


def parse_tweet_time(time_str: str) -> datetime:
    """解析 Twitter 时间字符串"""
    formats = [
        "%a %b %d %H:%M:%S %z %Y",  # Tue Mar 11 12:00:00 +0000 2026
        "%Y-%m-%dT%H:%M:%S.%fZ",    # 2026-03-11T12:00:00.000Z
        "%Y-%m-%dT%H:%M:%S.%f",     # 2026-03-11T12:00:00.000000
        "%Y-%m-%dT%H:%M:%S",        # 2026-03-11T12:00:00
        "%Y-%m-%d %H:%M:%S",        # 2026-03-11 12:00:00
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    return None


def filter_tweets_by_engagement(
    tweets: list[Tweet],
    min_likes: int = 0,
    min_retweets: int = 0,
    min_views: int = 0
) -> list[Tweet]:
    """根据互动数据筛选推文"""
    filtered = []
    
    for tweet in tweets:
        likes = getattr(tweet, 'like_count', None)
        if likes is None:
            likes = getattr(tweet, 'likes', 0)

        retweets = getattr(tweet, 'retweet_count', None)
        if retweets is None:
            retweets = getattr(tweet, 'retweets', 0)

        views = getattr(tweet, 'view_count', None)
        if views is None:
            views = getattr(tweet, 'views', 0)

        likes = likes or 0
        retweets = retweets or 0
        views = views or 0
        
        if likes >= min_likes and retweets >= min_retweets and views >= min_views:
            filtered.append(tweet)
    
    return filtered


def select_tweets(
    tweets: list[Tweet],
    mode: str = "random",
    count: int = 1,
    sort_by: str = "engagement"
) -> list[Tweet]:
    """
    选择推文
    
    Args:
        mode: 选择模式 (random, latest, top)
        count: 选择数量
        sort_by: 排序依据 (engagement, likes, retweets, views)
    """
    if not tweets:
        return []
    
    # 如果需要排序
    if sort_by != "random":
        def get_engagement(tweet):
            likes = getattr(tweet, 'like_count', None)
            if likes is None:
                likes = getattr(tweet, 'likes', 0)

            retweets = getattr(tweet, 'retweet_count', None)
            if retweets is None:
                retweets = getattr(tweet, 'retweets', 0)

            views = getattr(tweet, 'view_count', None)
            if views is None:
                views = getattr(tweet, 'views', 0)

            return (likes or 0) + (retweets or 0) * 2 + (views or 0) * 0.01
        
        if sort_by == "engagement":
            tweets.sort(key=get_engagement, reverse=True)
        elif sort_by == "likes":
            tweets.sort(
                key=lambda t: (getattr(t, 'like_count', None) or getattr(t, 'likes', 0) or 0),
                reverse=True
            )
        elif sort_by == "retweets":
            tweets.sort(
                key=lambda t: (getattr(t, 'retweet_count', None) or getattr(t, 'retweets', 0) or 0),
                reverse=True
            )
        elif sort_by == "views":
            tweets.sort(
                key=lambda t: (getattr(t, 'view_count', None) or getattr(t, 'views', 0) or 0),
                reverse=True
            )
    
    # 根据模式选择
    if mode == "random":
        selected = random.sample(tweets, min(count, len(tweets)))
    elif mode == "latest":
        selected = tweets[:count]
    elif mode == "top":
        selected = tweets[:count]
    else:
        selected = tweets[:count]
    
    return selected


# ============== 主工作流 ==============

async def run_workflow_async(config: dict, dry_run: bool = False, headless: bool = True):
    """
    执行主工作流（异步版本）
    """
    print(f"🚀 开始执行 Twitter 自动回复工作流")
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. 频率限制检查
    print("\n⏰ 步骤 1: 检查频率限制...")
    allowed, reason = check_rate_limit(config)
    
    if not allowed:
        print(f"   ⚠️  {reason}")
        print(f"   💡 提示：可以调整 config.json 中的 rate_limit 配置")
        return
    
    print(f"   ✅ {reason}")
    
    # 2. 初始化组件
    print("\n📋 步骤 2: 初始化组件...")
    
    volc_key = os.getenv("VOLC_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not volc_key:
        print("❌ 错误：VOLC_API_KEY 未设置")
        print("   请检查 .env 文件中的 VOLC_API_KEY 配置")
        sys.exit(1)
    if not telegram_token or not telegram_chat_id:
        print("❌ 错误：TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未设置")
        sys.exit(1)
    
    # 初始化爬虫
    search_config = config.get("search", {})
    scraper = TwitterScraper(headless=headless)
    await scraper.start()
    
    # 检查登录状态
    if not await scraper.is_logged_in():
        print("❌ Twitter 未登录，请先运行登录")
        print("   运行：python login_twitter.py")
        await scraper.close()
        sys.exit(1)
    
    generator = ReplyGenerator(api_key=volc_key)
    bot = TelegramBot(telegram_token, telegram_chat_id)
    
    print("✅ 组件初始化完成")
    
    # 3. 搜索推文
    print(f"\n🔍 步骤 3: 搜索推文...")
    query = search_config.get("query", "")
    time_range = search_config.get("time_range_hours", 24)
    
    print(f"   查询：{query}")
    print(f"   时间范围：{time_range} 小时内")
    print(f"   最小点赞：{search_config.get('min_likes', 0)}")
    print(f"   最小转发：{search_config.get('min_retweets', 0)}")
    print(f"   最小曝光：{search_config.get('min_views', 0)}")
    
    tweets = await scraper.search_tweets(
        query=query,
        max_results=50,  # 先获取较多推文用于筛选
        min_likes=search_config.get("min_likes", 0),
        min_retweets=search_config.get("min_retweets", 0)
    )
    
    print(f"   初始获取：{len(tweets)} 条推文")
    
    # 4. 筛选推文
    print(f"\n🎯 步骤 4: 筛选推文...")
    
    # 时间筛选
    if time_range > 0:
        tweets = filter_tweets_by_time(tweets, time_range)
        print(f"   时间筛选后：{len(tweets)} 条（{time_range}小时内）")
    
    # 互动数据筛选
    tweets = filter_tweets_by_engagement(
        tweets,
        min_likes=search_config.get("min_likes", 0),
        min_retweets=search_config.get("min_retweets", 0),
        min_views=search_config.get("min_views", 0)
    )
    print(f"   互动筛选后：{len(tweets)} 条")
    
    # 排除回复和转推
    if search_config.get("exclude_replies", True):
        tweets = [t for t in tweets if not getattr(t, 'is_reply', False)]
        print(f"   排除回复后：{len(tweets)} 条")
    
    if not tweets:
        print("✅ 没有符合条件的推文")
        await scraper.close()
        return
    
    # 5. 选择推文
    selection_config = config.get("selection", {})
    mode = selection_config.get("mode", "random")
    count = selection_config.get("count", 1)
    sort_by = selection_config.get("sort_by", "engagement")
    
    print(f"\n🎲 步骤 5: 选择推文（模式：{mode}, 数量：{count}）...")
    selected_tweets = select_tweets(tweets, mode, count, sort_by)
    print(f"   选中 {len(selected_tweets)} 条推文")
    
    # 6. 生成回复并发送
    print(f"\n💡 步骤 6: 生成回复并发送到 Telegram...")
    
    reply_config = config.get("reply", {})
    messages = []
    
    for i, tweet in enumerate(selected_tweets, 1):
        print(f"\n   [{i}/{len(selected_tweets)}] 处理推文：{tweet.id}")
        
        try:
            replies = generator.generate_replies(
                tweet_text=tweet.text,
                tweet_author=tweet.author_username,
                num_replies=3,
                custom_instructions=reply_config.get("custom_instructions", ""),
                language=reply_config.get("language", "中文")
            )
            
            print(f"       ✅ 生成 {len(replies)} 条回复")
            
            msg = TweetMessage(
                tweet_text=tweet.text,
                tweet_url=tweet.url,
                author=tweet.author_username,
                reply_options=[
                    {"style": r.style, "content": r.content}
                    for r in replies
                ]
            )
            messages.append(msg)
            
        except Exception as e:
            print(f"       ❌ 生成回复失败：{e}")
            continue
    
    # 7. 发送到 Telegram
    telegram_config = config.get("telegram", {})
    
    if not dry_run and telegram_config.get("enabled", True):
        print(f"\n📤 步骤 7: 发送 {len(messages)} 条消息到 Telegram...")
        
        if telegram_config.get("batch_send", False):
            success = bot.send_batch(messages, delay_between=2)
        else:
            success = 0
            for msg in messages:
                if bot.send_tweet_with_replies(msg):
                    success += 1
        
        print(f"   ✅ 成功发送 {success} 条消息")
    else:
        print(f"\n🧪 测试模式：不实际发送消息")
        for msg in messages:
            print(f"\n   预览消息:")
            print(f"   作者：@{msg.author}")
            print(f"   推文：{msg.tweet_text[:50]}...")
            print(f"   回复选项：{len(msg.reply_options)} 条")
    
    await scraper.close()
    
    # 更新频率限制状态
    update_rate_limit_state()
    
    # 保存已处理的推文 ID
    processed_ids = [t.id for t in selected_tweets]
    save_processed_tweets("processed_tweets.json", processed_ids)
    
    print(f"\n✅ 工作流执行完成！")
    print(f"   已处理 {len(processed_ids)} 条推文")
    print(f"   请查看 Telegram 消息并选择回复")


def save_processed_tweets(tweets_file: str, tweet_ids: list):
    """保存已处理的推文 ID，避免重复"""
    existing = []
    if os.path.exists(tweets_file):
        with open(tweets_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    # 只保留最近的 1000 条
    existing = (existing + tweet_ids)[-1000:]
    
    with open(tweets_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def run_workflow(config: dict, dry_run: bool = False, headless: bool = True):
    """同步包装器"""
    asyncio.run(run_workflow_async(config, dry_run, headless))


def main():
    parser = argparse.ArgumentParser(description="Twitter 自动回复工作流（增强版）")
    parser.add_argument(
        "-q", "--query",
        type=str,
        default="",
        help="Twitter 搜索查询语句"
    )
    parser.add_argument(
        "-n", "--num-tweets",
        type=int,
        default=0,
        help="选择推文数量（0 表示使用配置文件）"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=0,
        help="时间范围（小时），0 表示使用配置文件"
    )
    parser.add_argument(
        "--min-likes",
        type=int,
        default=0,
        help="最小点赞数，0 表示使用配置文件"
    )
    parser.add_argument(
        "--min-views",
        type=int,
        default=0,
        help="最小曝光量，0 表示使用配置文件"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["random", "latest", "top"],
        default="",
        help="选择模式（random/latest/top）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="测试模式，不实际发送消息"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="显示浏览器窗口（默认无头模式）"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="配置文件路径"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="显示当前配置"
    )
    parser.add_argument(
        "--check-rate",
        action="store_true",
        help="检查频率限制状态"
    )
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 显示配置
    if args.show_config:
        print("当前配置:")
        print(json.dumps(config, ensure_ascii=False, indent=2))
        return
    
    # 检查频率限制状态
    if args.check_rate:
        allowed, reason = check_rate_limit(config)
        state = load_rate_limit_state()
        print(f"频率限制状态:")
        print(f"  最后运行：{state.get('last_run', '从未')}")
        print(f"  今日运行：{state.get('runs_today', 0)} 次")
        print(f"  本小时运行：{state.get('runs_this_hour', 0)} 次")
        print(f"  检查结果：{'✅ 允许运行' if allowed else '❌ 禁止运行'} - {reason}")
        return
    
    # 命令行参数覆盖配置
    if args.query:
        config["search"]["query"] = args.query
    if args.hours > 0:
        config["search"]["time_range_hours"] = args.hours
    if args.min_likes > 0:
        config["search"]["min_likes"] = args.min_likes
    if args.min_views > 0:
        config["search"]["min_views"] = args.min_views
    if args.num_tweets > 0:
        config["selection"]["count"] = args.num_tweets
    if args.mode:
        config["selection"]["mode"] = args.mode
    
    # 运行工作流
    run_workflow(
        config=config,
        dry_run=args.dry_run,
        headless=not args.visible
    )


if __name__ == "__main__":
    main()
