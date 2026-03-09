#!/usr/bin/env python3
"""
Twitter 登录脚本

首次使用时运行，登录 Twitter 并保存 Cookie
之后无需再次登录
"""

import asyncio
from twitter_scraper import TwitterScraper


async def main():
    print("=" * 50)
    print("Twitter 登录工具")
    print("=" * 50)
    
    scraper = TwitterScraper(headless=False)  # 显示浏览器
    
    try:
        await scraper.start()
        
        # 检查是否已经登录
        print("\n📱 正在打开 Twitter...")
        await scraper.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        current_url = scraper.page.url
        if "login" not in current_url and "i/flow/login" not in current_url:
            print("✅ 检测到已登录状态")
            save = input("是否保存当前 Cookie？(y/n): ")
            if save.lower() == 'y':
                await scraper.save_cookies()
                print("✅ Cookie 已保存")
            else:
                print("❌ 未保存")
        else:
            print("\n📱 请在浏览器中登录 Twitter")
            print("   支持以下登录方式:")
            print("   - 邮箱/手机号 + 密码")
            print("   - Google 账号")
            print("   - Apple 账号")
            print("\n   登录完成后按回车键保存 Cookie...")
            input()
            await scraper.save_cookies()
            print("\n✅ Cookie 已保存到 twitter_cookies.json")
            print("   下次运行工作流时无需再次登录")
        
        # 验证登录
        if await scraper.is_logged_in():
            print("\n✅ 登录验证成功！")
        else:
            print("\n⚠️  登录验证失败，请重试")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
