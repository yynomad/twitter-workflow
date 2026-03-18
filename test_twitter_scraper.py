#!/usr/bin/env python3
"""
Twitter 爬虫测试
测试搜索推文功能
"""

import asyncio
import sys
from twitter_scraper import TwitterScraper


async def test_search_tweets():
    """测试搜索推文"""
    print("=" * 60)
    print("🧪 测试：Twitter 搜索推文")
    print("=" * 60)
    
    scraper = TwitterScraper(headless=True)
    
    try:
        # 启动浏览器
        print("\n1️⃣ 启动浏览器...")
        await scraper.start()
        
        # 检查登录状态
        print("2️⃣ 检查登录状态...")
        if not await scraper.is_logged_in():
            print("❌ 失败：Twitter 未登录")
            print("   请先运行：python main.py --login")
            return False
        print("   ✅ 已登录")
        
        # 测试搜索 - 新条件：近 4 小时，views>500k, 评论<200
        print("\n3️⃣ 测试搜索：AI OR 人工智能")
        print("   条件：近 4 小时，views>500k, 评论<200")
        tweets = await scraper.search_tweets(
            query="AI OR 人工智能",
            max_results=5,
            min_likes=0,
            min_views=500000,
            max_replies=200
        )
        
        print(f"\n📊 搜索结果：{len(tweets)} 条推文")
        
        if len(tweets) == 0:
            print("⚠️  警告：未找到推文")
            print("   可能原因：")
            print("   - Cookie 过期，请重新登录")
            print("   - 搜索条件太严格，尝试降低 min_likes")
            return False
        
        # 显示前 3 条推文详情
        print("\n📝 推文详情（前 3 条）：")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"\n   [{i}] @{tweet.author_username}")
            print(f"       内容：{tweet.text[:100]}...")
            print(f"       点赞：{tweet.like_count}")
            print(f"       转发：{tweet.retweet_count}")
            print(f"       评论：{tweet.reply_count}")
            print(f"       浏览：{tweet.view_count}")
            print(f"       链接：{tweet.url}")
        
        print("\n✅ 测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await scraper.close()


async def test_filter_by_time():
    """测试时间筛选"""
    from datetime import datetime, timedelta
    from main import filter_tweets_by_time
    
    print("\n" + "=" * 60)
    print("🧪 测试：时间筛选功能")
    print("=" * 60)
    
    # 创建测试数据
    now = datetime.now()
    test_tweets = [
        type('Tweet', (), {
            'created_at': (now - timedelta(hours=1)).isoformat()
        })(),
        type('Tweet', (), {
            'created_at': (now - timedelta(hours=12)).isoformat()
        })(),
        type('Tweet', (), {
            'created_at': (now - timedelta(hours=48)).isoformat()
        })(),
    ]
    
    # 测试 24 小时筛选
    filtered = filter_tweets_by_time(test_tweets, 24)
    print(f"\n24 小时内：{len(filtered)}/3 条")
    
    if len(filtered) == 2:
        print("✅ 时间筛选正常")
        return True
    else:
        print("❌ 时间筛选异常")
        return False


async def main():
    """运行所有测试"""
    print("\n🚀 Twitter 爬虫测试套件\n")
    
    results = []
    
    # 测试 1: 搜索推文
    results.append(await test_search_tweets())
    
    # 测试 2: 时间筛选
    results.append(await test_filter_by_time())
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过：{passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
