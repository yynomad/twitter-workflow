#!/usr/bin/env python3
"""
调试脚本：在 Mac 上真实打开浏览器，查看 views 是否能获取

使用方法:
  python3 debug_views.py

在 Mac 上运行时，会真实打开浏览器窗口，你可以：
1. 肉眼确认推文有没有显示 views
2. 用开发者工具检查 DOM 结构
3. 手动滚动页面
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def debug_views():
    """调试 views 获取"""
    print("=" * 60)
    print("🔬 调试：Twitter Views 获取")
    print("=" * 60)
    print("\n💡 提示:")
    print("   1. 浏览器会真实打开，不要关闭")
    print("   2. 可以按 F12 打开开发者工具")
    print("   3. 检查推文底部有没有显示浏览数")
    print("   4. 按回车键继续下一步\n")
    
    playwright = await async_playwright().start()
    
    # 启动浏览器（显示窗口）
    browser = await playwright.chromium.launch(
        headless=False,  # 真实显示窗口
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    
    # 加载 Cookie
    import os
    cookie_file = "twitter_cookies.json"
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print(f"✅ 已加载 Cookie")
    
    page = await context.new_page()
    
    # 跳转到 Twitter 搜索
    query = "AI"
    import urllib.parse
    encoded_query = urllib.parse.quote(f"{query} -filter:replies -filter:retweets")
    url = f"https://twitter.com/search?q={encoded_query}&f=live"
    
    print(f"\n🔍 打开搜索：{url}")
    await page.goto(url, wait_until="domcontentloaded")
    
    input("\n⏸️  页面已打开，请检查：")
    print("   1. 推文底部有没有显示浏览数？（如 '1.5K views' 或 '1.5 万回表示'）")
    print("   2. 如果有，鼠标悬停在上面，看看 DOM 结构是什么")
    print("   3. 按回车继续...")
    
    # 滚动页面
    print("\n📜 开始滚动页面，加载更多内容...")
    for i in range(5):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        print(f"   滚动 {i+1}/5")
    
    input("\n⏸️  页面已滚动，按回车查看抓取结果...")
    
    # 提取推文数据
    print("\n🔍 尝试提取 views 数据...")
    
    articles = page.locator('article[data-testid="tweet"]')
    count = await articles.count()
    print(f"   找到 {count} 条推文")
    
    for i in range(min(5, count)):
        print(f"\n--- 推文 {i+1} ---")
        article = articles.nth(i)
        
        # 获取推文文本
        text_elem = article.locator('div[data-testid="tweetText"]')
        if await text_elem.count() > 0:
            text = await text_elem.first.inner_text()
            print(f"   内容：{text[:60]}...")
        
        # 尝试多种方式获取 views
        print("   尝试获取 views:")
        
        # 方法 1: 查找包含 "views" 的 span
        for pattern in ["views", "回表示", "Vues", "Vistas"]:
            elem = article.locator(f'span:has-text("{pattern}")')
            if await elem.count() > 0:
                view_text = await elem.first.inner_text()
                print(f"      ✅ 找到 [{pattern}]: {view_text}")
            else:
                print(f"      ❌ 未找到 [{pattern}]")
        
        # 方法 2: 查找 analytics 图标
        analytics = article.locator('svg[data-testid="analyticsIcon"]')
        if await analytics.count() > 0:
            print(f"      ✅ 找到 analytics 图标")
            # 尝试获取父元素
            try:
                parent = analytics.locator('xpath=..')
                parent_text = await parent.inner_text()
                print(f"         父元素文本：{parent_text}")
            except Exception as e:
                print(f"         无法获取父元素文本：{e}")
        else:
            print(f"      ❌ 未找到 analytics 图标")
        
        # 方法 3: 获取整个底部互动栏
        footer = article.locator('footer[role="group"]')
        if await footer.count() > 0:
            footer_text = await footer.inner_text()
            print(f"      互动栏文本：{footer_text[:100]}")
    
    print("\n" + "=" * 60)
    print("📝 下一步:")
    print("   1. 如果看到 views 但脚本没抓到，告诉我 DOM 结构")
    print("   2. 按 F12 打开开发者工具，右键 views 元素 → Inspect")
    print("   3. 复制 HTML 代码，我可以更新选择器")
    print("=" * 60)
    
    input("\n按回车关闭浏览器...")
    
    await browser.close()
    print("✅ 调试完成")


if __name__ == "__main__":
    asyncio.run(debug_views())
