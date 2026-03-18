#!/usr/bin/env python3
"""
调试：检查推文互动数据的选择器
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright


async def debug_extraction():
    playwright = await async_playwright().start()
    
    browser = await playwright.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    
    # 加载 Cookie
    cookie_file = "twitter_cookies.json"
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
    
    page = await context.new_page()
    
    # 检查登录状态
    print("🔍 检查登录状态...")
    await page.goto("https://twitter.com/home", wait_until="domcontentloaded")
    await asyncio.sleep(2)
    
    if "login" in page.url:
        print("❌ 未登录，请重新运行：python main.py --login")
        await browser.close()
        return
    print("✅ 已登录")
    
    # 搜索
    import urllib.parse
    query = "AI"
    encoded_query = urllib.parse.quote(f"{query} -filter:replies -filter:retweets")
    url = f"https://twitter.com/search?q={encoded_query}&f=live"
    
    print(f"\n🔍 搜索：{url}")
    await page.goto(url, wait_until="domcontentloaded")
    await asyncio.sleep(5)  # 多等一会
    
    # 滚动
    print("📜 滚动页面...")
    for i in range(5):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
    
    # 检查第一条推文
    print("\n🔍 检查第一条推文...")
    article = page.locator('article[data-testid="tweet"]').first
    
    if await article.count() == 0:
        print("❌ 未找到推文")
        return
    
    # 获取推文文本
    text = await article.locator('div[data-testid="tweetText"]').inner_text()
    print(f"\n📝 内容：{text[:100]}...")
    
    # 尝试所有可能的选择器
    print("\n🔍 尝试各种互动数据选择器:")
    
    selectors = {
        "点赞": [
            'div[data-testid="like"]',
            'div[role="button"]:has-text("Like")',
            '[data-testid="like"]',
        ],
        "回复": [
            'div[data-testid="reply"]',
            'div[role="button"]:has-text("Reply")',
            '[data-testid="reply"]',
        ],
        "转发": [
            'div[data-testid="retweet"]',
            'div[role="button"]:has-text("Repost")',
            '[data-testid="retweet"]',
        ],
        "浏览": [
            'span:has-text("views")',
            'span:has-text("回表示")',
            '[data-testid="analytics"]',
        ]
    }
    
    for interaction, selector_list in selectors.items():
        print(f"\n{interaction}:")
        for selector in selector_list:
            try:
                elem = article.locator(selector)
                count = await elem.count()
                if count > 0:
                    text = await elem.first.inner_text()
                    print(f"   ✅ {selector}: '{text}'")
                else:
                    print(f"   ❌ {selector}: 未找到")
            except Exception as e:
                print(f"   ❌ {selector}: {e}")
    
    # 获取整个底部栏
    print("\n🔍 获取整个互动栏:")
    footer = article.locator('footer[role="group"]')
    if await footer.count() > 0:
        footer_text = await footer.inner_text()
        print(f"   底部栏文本：{footer_text}")
        
        # 获取所有按钮
        buttons = footer.locator('div[role="button"]')
        btn_count = await buttons.count()
        print(f"   按钮数量：{btn_count}")
        
        for i in range(min(btn_count, 5)):
            btn = buttons.nth(i)
            btn_text = await btn.inner_text()
            print(f"   按钮{i+1}: '{btn_text}'")
    
    # 获取 HTML 片段
    print("\n🔍 获取推文 HTML 片段:")
    html = await article.evaluate('el => el.outerHTML')
    print(f"   HTML 长度：{len(html)}")
    
    # 保存到文件
    with open('tweet_html_debug.txt', 'w', encoding='utf-8') as f:
        f.write(html)
    print("   ✅ HTML 已保存到：tweet_html_debug.txt")
    
    await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_extraction())
