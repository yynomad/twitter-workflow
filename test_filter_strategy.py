#!/usr/bin/env python3
"""
测试筛选策略：min_likes + max_replies

结论：
- views: Twitter 不总是显示，作为辅助参考
- min_likes + max_replies: 可靠，推荐作为主要筛选条件
"""

import asyncio
import sys
from twitter_scraper import TwitterScraper


async def test_filter_strategy():
    """测试不同筛选策略"""
    print("=" * 60)
    print("🧪 测试：筛选策略对比")
    print("=" * 60)
    
    scraper = TwitterScraper(headless=True)
    
    try:
        print("\n1️⃣ 启动浏览器...")
        await scraper.start()
        
        print("2️⃣ 检查登录状态...")
        if not await scraper.is_logged_in():
            print("❌ Twitter 未登录")
            return False
        print("   ✅ 已登录")
        
        # 策略 1: 只限制 min_likes
        print("\n" + "=" * 60)
        print("策略 1: min_likes >= 50")
        print("=" * 60)
        tweets1 = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=50,
            min_views=0,
            max_replies=999999
        )
        
        print(f"\n📊 结果：{len(tweets1)} 条")
        for i, tweet in enumerate(tweets1[:3], 1):
            print(f"   [{i}] @{tweet.author_username}: 👍{tweet.like_count} 💬{tweet.reply_count} 👁️{tweet.view_count}")
        
        # 策略 2: min_likes + max_replies
        print("\n" + "=" * 60)
        print("策略 2: min_likes >= 50 AND max_replies <= 200 ⭐ 推荐")
        print("=" * 60)
        tweets2 = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=50,
            min_views=0,
            max_replies=200
        )
        
        print(f"\n📊 结果：{len(tweets2)} 条")
        for i, tweet in enumerate(tweets2[:3], 1):
            print(f"   [{i}] @{tweet.author_username}: 👍{tweet.like_count} 💬{tweet.reply_count} 👁️{tweet.view_count}")
        
        # 策略 3: 严格条件
        print("\n" + "=" * 60)
        print("策略 3: min_likes >= 100 AND max_replies <= 100")
        print("=" * 60)
        tweets3 = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=100,
            min_views=0,
            max_replies=100
        )
        
        print(f"\n📊 结果：{len(tweets3)} 条")
        for i, tweet in enumerate(tweets3[:3], 1):
            print(f"   [{i}] @{tweet.author_username}: 👍{tweet.like_count} 💬{tweet.reply_count} 👁️{tweet.view_count}")
        
        # 策略 4: 尝试 views 筛选（如果有的话）
        print("\n" + "=" * 60)
        print("策略 4: min_likes >= 50 AND min_views >= 10000 (如果有 views)")
        print("=" * 60)
        tweets4 = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=50,
            min_views=10000,
            max_replies=200
        )
        
        print(f"\n📊 结果：{len(tweets4)} 条")
        if tweets4:
            for i, tweet in enumerate(tweets4[:3], 1):
                print(f"   [{i}] @{tweet.author_username}: 👍{tweet.like_count} 💬{tweet.reply_count} 👁️{tweet.view_count}")
        else:
            print("   (无结果 - Twitter 可能未显示 views)")
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"策略 1 (仅 min_likes):     {len(tweets1)} 条")
        print(f"策略 2 (min_likes+max_replies): {len(tweets2)} 条 ⭐ 推荐")
        print(f"策略 3 (严格):            {len(tweets3)} 条")
        print(f"策略 4 (含 views):         {len(tweets4)} 条")
        
        print("\n💡 结论:")
        print("   ✅ min_likes + max_replies 是最可靠的筛选组合")
        print("   ⚠️  views 不总是显示，仅作为辅助参考")
        print("   📝 推荐配置:")
        print("      - min_likes: 50-100 (根据热门程度调整)")
        print("      - max_replies: 100-200 (避免争议话题)")
        print("      - time_range_hours: 4-24 (根据时效性调整)")
        
        # 验证筛选逻辑
        if tweets2:
            print("\n✅ 验证筛选结果:")
            all_valid = True
            for tweet in tweets2:
                if tweet.like_count < 50:
                    print(f"   ❌ @{tweet.author_username}: 点赞{tweet.like_count} < 50")
                    all_valid = False
                if tweet.reply_count > 200:
                    print(f"   ❌ @{tweet.author_username}: 评论{tweet.reply_count} > 200")
                    all_valid = False
            
            if all_valid:
                print("   ✅ 所有推文都符合筛选条件！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_filter_strategy())
