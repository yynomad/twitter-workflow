#!/usr/bin/env python3
"""
Twitter 自动回复工作流 - 主脚本（Playwright 版本）

流程：
1. 使用 Playwright 浏览器自动化搜索 Twitter 推文
2. 为每条推文生成 3 条回复
3. 通过 Telegram 发送推文内容和回复选项
4. 用户手动点击链接并复制回复到评论区
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from twitter_scraper import TwitterScraper, Tweet
from reply_generator import ReplyGenerator
from telegram_bot import TelegramBot, TweetMessage


def load_config(config_file: str = "config.json") -> dict:
    """加载配置文件"""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


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


def load_processed_tweets(tweets_file: str) -> set:
    """加载已处理的推文 ID"""
    if os.path.exists(tweets_file):
        with open(tweets_file, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()


async def run_workflow_async(
    search_query: str,
    max_tweets: int = 5,
    min_likes: int = 0,
    min_retweets: int = 0,
    custom_instructions: str = "",
    language: str = "中文",
    dry_run: bool = False,
    headless: bool = True
):
    """
    执行主工作流（异步版本）
    """
    print(f"🚀 开始执行 Twitter 自动回复工作流")
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. 初始化组件
    print("\n📋 步骤 1: 初始化组件...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not openai_key:
        print("❌ 错误：OPENAI_API_KEY 未设置")
        sys.exit(1)
    if not telegram_token or not telegram_chat_id:
        print("❌ 错误：TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未设置")
        sys.exit(1)
    
    # 初始化爬虫
    scraper = TwitterScraper(headless=headless)
    await scraper.start()
    
    # 检查登录状态
    if not await scraper.is_logged_in():
        print("❌ Twitter 未登录，请先运行登录")
        print("   运行：python login_twitter.py")
        await scraper.close()
        sys.exit(1)
    
    generator = ReplyGenerator(api_key=openai_key)
    bot = TelegramBot(telegram_token, telegram_chat_id)
    
    print("✅ 组件初始化完成")
    
    # 2. 搜索推文
    print(f"\n🔍 步骤 2: 搜索推文...")
    print(f"   查询：{search_query}")
    print(f"   最小点赞：{min_likes}, 最小转发：{min_retweets}")
    
    tweets = await scraper.search_tweets(
        query=search_query,
        max_results=max_tweets * 2,
        min_likes=min_likes,
        min_retweets=min_retweets
    )
    
    # 过滤已处理的推文
    processed = load_processed_tweets("processed_tweets.json")
    new_tweets = [t for t in tweets if t.id not in processed]
    
    if not new_tweets:
        print("✅ 没有新的推文需要处理")
        await scraper.close()
        return
    
    print(f"   找到 {len(tweets)} 条推文，{len(new_tweets)} 条未处理")
    
    # 3. 生成回复并发送
    print(f"\n💡 步骤 3: 生成回复并发送到 Telegram...")
    
    messages = []
    processed_ids = []
    
    for i, tweet in enumerate(new_tweets[:max_tweets], 1):
        print(f"\n   [{i}/{max_tweets}] 处理推文：{tweet.id}")
        
        try:
            replies = generator.generate_replies(
                tweet_text=tweet.text,
                tweet_author=tweet.author_username,
                num_replies=3,
                custom_instructions=custom_instructions,
                language=language
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
            processed_ids.append(tweet.id)
            
        except Exception as e:
            print(f"       ❌ 生成回复失败：{e}")
            continue
    
    # 4. 发送到 Telegram
    if not dry_run:
        print(f"\n📤 步骤 4: 发送 {len(messages)} 条消息到 Telegram...")
        success = bot.send_batch(messages, delay_between=2)
        print(f"   ✅ 成功发送 {success} 条消息")
    else:
        print(f"\n🧪 测试模式：不实际发送消息")
        for msg in messages:
            print(f"\n   预览消息:")
            print(f"   作者：@{msg.author}")
            print(f"   推文：{msg.tweet_text[:50]}...")
            print(f"   回复选项：{len(msg.reply_options)} 条")
    
    await scraper.close()
    
    # 保存已处理的推文 ID
    save_processed_tweets("processed_tweets.json", processed_ids)
    print(f"\n✅ 工作流执行完成！")
    print(f"   已处理 {len(processed_ids)} 条推文")
    print(f"   请查看 Telegram 消息并选择回复")


def run_workflow(
    search_query: str,
    max_tweets: int = 5,
    min_likes: int = 0,
    min_retweets: int = 0,
    custom_instructions: str = "",
    language: str = "中文",
    dry_run: bool = False,
    headless: bool = True
):
    """同步包装器"""
    asyncio.run(run_workflow_async(
        search_query=search_query,
        max_tweets=max_tweets,
        min_likes=min_likes,
        min_retweets=min_retweets,
        custom_instructions=custom_instructions,
        language=language,
        dry_run=dry_run,
        headless=headless
    ))


def main():
    parser = argparse.ArgumentParser(description="Twitter 自动回复工作流")
    parser.add_argument(
        "-q", "--query",
        type=str,
        default="",
        help="Twitter 搜索查询语句"
    )
    parser.add_argument(
        "-n", "--num-tweets",
        type=int,
        default=5,
        help="最大处理推文数 (默认：5)"
    )
    parser.add_argument(
        "--min-likes",
        type=int,
        default=0,
        help="最小点赞数 (默认：0)"
    )
    parser.add_argument(
        "--min-retweets",
        type=int,
        default=0,
        help="最小转发数 (默认：0)"
    )
    parser.add_argument(
        "--instructions",
        type=str,
        default="",
        help="回复生成自定义指令"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="中文",
        help="回复语言 (默认：中文)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="测试模式，不实际发送消息"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="显示浏览器窗口 (默认无头模式)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="配置文件路径"
    )
    
    args = parser.parse_args()
    
    # 加载配置文件
    config = load_config(args.config)
    
    # 使用配置文件中的查询语句（如果命令行未指定）
    search_query = args.query or config.get("search_query", "")
    
    if not search_query:
        print("❌ 错误：请提供搜索查询语句")
        print("\n使用方式:")
        print("  1. 命令行参数：python main.py -q 'your search query'")
        print("  2. 配置文件：在 config.json 中设置 search_query")
        print("\n示例:")
        print("  python main.py -q 'AI OR 人工智能 min_faves:10'")
        sys.exit(1)
    
    run_workflow(
        search_query=search_query,
        max_tweets=args.num_tweets,
        min_likes=args.min_likes,
        min_retweets=args.min_retweets,
        custom_instructions=args.instructions,
        language=args.language,
        dry_run=args.dry_run,
        headless=not args.visible
    )


if __name__ == "__main__":
    main()
