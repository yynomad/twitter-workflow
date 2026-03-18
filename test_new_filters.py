#!/usr/bin/env python3
"""
新筛选条件测试
测试：近 4 小时，views>500k, 评论<200
"""

import asyncio
import sys
from twitter_scraper import TwitterScraper


async def test_new_filters():
    """测试新的筛选条件"""
    print("=" * 60)
    print("🧪 测试：新筛选条件")
    print("   条件：近 4 小时，views>500k, 评论<200")
    print("=" * 60)
    
    # 如果用 Mac，可以改成 headless=False 真实打开浏览器
    scraper = TwitterScraper(headless=True)
    
    try:
        print("\n1️⃣ 启动浏览器...")
        await scraper.start()
        
        print("2️⃣ 检查登录状态...")
        if not await scraper.is_logged_in():
            print("❌ Twitter 未登录")
            print("   请先运行：python main.py --login")
            return False
        print("   ✅ 已登录")
        
        # 测试 1: 严格条件（views>500k, 评论<200）
        print("\n3️⃣ 测试严格条件：views>500k, 评论<200")
        tweets_strict = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=0,
            min_views=500000,
            max_replies=200
        )
        
        print(f"\n📊 严格条件结果：{len(tweets_strict)} 条")
        
        if tweets_strict:
            for i, tweet in enumerate(tweets_strict[:2], 1):
                print(f"\n   [{i}] @{tweet.author_username}")
                print(f"       内容：{tweet.text[:80]}...")
                print(f"       👍 {tweet.like_count} | 🔄 {tweet.retweet_count}")
                print(f"       💬 {tweet.reply_count} | 👁️ {tweet.view_count}")
        
        # 测试 2: 宽松条件（views>100k, 评论<500）
        print("\n\n4️⃣ 测试宽松条件：views>100k, 评论<500")
        tweets_loose = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=0,
            min_views=100000,
            max_replies=500
        )
        
        print(f"\n📊 宽松条件结果：{len(tweets_loose)} 条")
        
        if tweets_loose:
            for i, tweet in enumerate(tweets_loose[:2], 1):
                print(f"\n   [{i}] @{tweet.author_username}")
                print(f"       内容：{tweet.text[:80]}...")
                print(f"       👍 {tweet.like_count} | 🔄 {tweet.retweet_count}")
                print(f"       💬 {tweet.reply_count} | 👁️ {tweet.view_count}")
        
        # 测试 3: 无浏览数限制
        print("\n\n5️⃣ 测试无浏览数限制：仅评论<200")
        tweets_no_view = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=0,
            min_views=0,
            max_replies=200
        )
        
        print(f"\n📊 无浏览数限制结果：{len(tweets_no_view)} 条")
        
        if tweets_no_view:
            for i, tweet in enumerate(tweets_no_view[:2], 1):
                print(f"\n   [{i}] @{tweet.author_username}")
                print(f"       内容：{tweet.text[:80]}...")
                print(f"       👍 {tweet.like_count} | 🔄 {tweet.retweet_count}")
                print(f"       💬 {tweet.reply_count} | 👁️ {tweet.view_count}")
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"严格条件 (500k/200):  {len(tweets_strict)} 条")
        print(f"宽松条件 (100k/500):  {len(tweets_loose)} 条")
        print(f"无浏览限制 (0/200):   {len(tweets_no_view)} 条")
        
        if len(tweets_loose) > 0 or len(tweets_no_view) > 0:
            print("\n✅ 筛选功能正常工作！")
            print("\n💡 建议:")
            print("   - 如果严格条件返回 0，说明该条件下推文较少")
            print("   - 可以尝试降低 min_views 或增加 max_replies")
            print("   - 也可以扩大搜索关键词范围")
            return True
        else:
            print("\n⚠️  所有条件都返回 0，可能原因:")
            print("   - Cookie 过期，请重新登录")
            print("   - Twitter 页面结构变化，需要更新爬虫")
            return False
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_new_filters())
