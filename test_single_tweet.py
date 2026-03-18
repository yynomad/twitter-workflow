#!/usr/bin/env python3
"""
测试抓取单条推文
验证所有字段（包括 views）是否能正确获取
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright


async def test_single_tweet():
    """测试抓取单条推文"""
    print("=" * 60)
    print("🧪 测试：抓取单条推文")
    print("=" * 60)
    
    playwright = await async_playwright().start()
    
    # 启动浏览器
    # 注意：服务器环境只能用 headless=True
    # 在 Mac 本地运行时可以改成 headless=False
    browser = await playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    
    # 加载 Cookie
    cookie_file = "twitter_cookies.json"
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print(f"✅ 已加载 Cookie")
    
    page = await context.new_page()
    
    # 方法 1: 打开特定推文 URL
    # 找一条热门推文（这里用示例 URL，可以替换成实际的）
    # tweet_url = "https://twitter.com/elonmusk/status/1234567890"
    
    # 方法 2: 搜索并抓取第一条 - 使用更严格的条件找热门推文
    import urllib.parse
    
    # 搜索条件：热门推文（点赞>100，排除回复和转推）
    query = "AI min_faves:100"
    encoded_query = urllib.parse.quote(f"{query} -filter:replies -filter:retweets")
    url = f"https://twitter.com/search?q={encoded_query}&f=live"
    
    print(f"\n🔍 搜索：{url}")
    await page.goto(url, wait_until="domcontentloaded")
    
    print("\n⏳ 等待页面加载...")
    await asyncio.sleep(3)
    
    # 滚动加载
    print("📜 滚动页面...")
    for i in range(5):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
    
    # 提取第一条推文
    print("\n🔍 提取第一条推文...")
    
    article = page.locator('article[data-testid="tweet"]').first
    
    if await article.count() == 0:
        print("❌ 未找到推文")
        await browser.close()
        return
    
    # 提取所有字段
    print("\n" + "=" * 60)
    print("📊 推文详情")
    print("=" * 60)
    
    # 1. 文本
    text_elem = article.locator('div[data-testid="tweetText"]')
    text = await text_elem.inner_text() if await text_elem.count() > 0 else "N/A"
    print(f"\n📝 内容:\n{text[:200]}...")
    
    # 2. 作者
    user_elem = article.locator('a[href^="/"][href*="/status"]').first
    username = "N/A"
    if await user_elem.count() > 0:
        href = await user_elem.get_attribute('href')
        username = href.split('/')[1] if href else "N/A"
    print(f"\n👤 作者：@{username}")
    
    # 3. 互动数据
    print("\n📈 互动数据:")
    
    # 点赞
    like_elem = article.locator('div[data-testid="like"]')
    like_count = 0
    if await like_elem.count() > 0:
        like_text = await like_elem.first.inner_text()
        like_count = parse_count(like_text)
        print(f"   👍 点赞：{like_text} ({like_count})")
    
    # 转发
    retweet_elem = article.locator('div[data-testid="retweet"]')
    retweet_count = 0
    if await retweet_elem.count() > 0:
        retweet_text = await retweet_elem.first.inner_text()
        retweet_count = parse_count(retweet_text)
        print(f"   🔄 转发：{retweet_text} ({retweet_count})")
    
    # 回复
    reply_elem = article.locator('div[data-testid="reply"]')
    reply_count = 0
    if await reply_elem.count() > 0:
        reply_text = await reply_elem.first.inner_text()
        reply_count = parse_count(reply_text)
        print(f"   💬 回复：{reply_text} ({reply_count})")
    
    # 浏览数 - 多种尝试
    print("\n👁️ 浏览数:")
    view_count = 0
    
    # 方法 1: 查找包含 "views" 的 span
    for pattern in ["views", "回表示", "Vues", "Vistas", "Aufrufe"]:
        view_elem = article.locator(f'span:has-text("{pattern}")')
        if await view_elem.count() > 0:
            view_text = await view_elem.first.inner_text()
            view_count = parse_count(view_text)
            print(f"   ✅ 找到 [{pattern}]: {view_text} ({view_count})")
            break
    else:
        print(f"   ❌ 未找到 views 元素")
    
    # 方法 2: 查找 analytics 图标
    analytics = article.locator('svg[data-testid="analyticsIcon"]')
    if await analytics.count() > 0:
        print(f"   ✅ 找到 analytics 图标")
        try:
            parent = analytics.locator('xpath=..')
            parent_text = await parent.inner_text()
            print(f"      父元素：{parent_text}")
        except Exception as e:
            print(f"      无法获取父元素：{e}")
    
    # 方法 3: 获取整个底部栏
    footer = article.locator('footer[role="group"]')
    if await footer.count() > 0:
        footer_text = await footer.inner_text()
        print(f"   底部栏：{footer_text}")
    
    # 4. 链接和 ID
    status_links = article.locator('a[href*="/status/"]')
    tweet_url = ""
    tweet_id = ""
    for j in range(await status_links.count()):
        link = await status_links.nth(j).get_attribute('href')
        if '/status/' in link:
            tweet_url = f"https://twitter.com{link}"
            tweet_id = link.split('/status/')[-1].split('?')[0]
            break
    
    print(f"\n🔗 链接：{tweet_url}")
    print(f"🆔 ID: {tweet_id}")
    
    # 5. 时间
    time_elem = article.locator('time')
    created_at = "N/A"
    if await time_elem.count() > 0:
        created_at = await time_elem.first.get_attribute('datetime')
    print(f"📅 时间：{created_at}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 抓取结果总结")
    print("=" * 60)
    print(f"✅ 内容：{'OK' if text != 'N/A' else 'FAIL'}")
    print(f"✅ 作者：{'OK' if username != 'N/A' else 'FAIL'}")
    print(f"✅ 点赞：{like_count}")
    print(f"✅ 转发：{retweet_count}")
    print(f"✅ 回复：{reply_count}")
    print(f"{'✅' if view_count > 0 else '❌'} 浏览：{view_count}")
    print(f"✅ 链接：{'OK' if tweet_url else 'FAIL'}")
    
    print("\n💡 提示:")
    print("   - 如果 views 显示 ❌，说明这条推文没有显示浏览数")
    print("   - 可以尝试其他推文，或者搜索更热门的关键词")
    print("   - 在 Mac 上运行可改 headless=False 用浏览器检查 DOM")
    
    await browser.close()
    print("\n✅ 测试完成")


def parse_count(text: str) -> int:
    """解析数字（1.5K, 2M 等）"""
    if not text:
        return 0
    
    text = text.replace(',', '').strip()
    multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    
    for suffix, mult in multipliers.items():
        if suffix in text.upper():
            try:
                return int(float(text.upper().replace(suffix, '')) * mult)
            except:
                return 0
    
    try:
        return int(text)
    except:
        return 0


if __name__ == "__main__":
    asyncio.run(test_single_tweet())
