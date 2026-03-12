#!/usr/bin/env python3
"""
Twitter Cookie 导入工具

使用方法：
1. 在浏览器中登录 Twitter
2. 复制 Cookie
3. 运行此脚本导入 Cookie
"""

import asyncio
import json
import os
from twitter_scraper import TwitterScraper


def get_cookie_from_user():
    """从用户输入获取 Cookie"""
    print("=" * 60)
    print("Twitter Cookie 导入工具")
    print("=" * 60)
    print()
    print("请按以下步骤获取 Twitter Cookie：")
    print()
    print("1. 在浏览器中打开 https://twitter.com/home")
    print("2. 登录你的 Twitter 账号")
    print("3. 按 F12 打开开发者工具")
    print("4. 切换到 Network（网络）标签")
    print("5. 刷新页面")
    print("6. 点击任意 twitter.com 的请求")
    print("7. 在 Request Headers 中找到 'Cookie:'")
    print("8. 复制整个 Cookie 字符串")
    print()
    print("或者使用浏览器扩展（推荐）：")
    print("- Chrome: 'EditThisCookie' 或 'Cookie Editor'")
    print("- Firefox: 'Cookie Quick Manager'")
    print("安装扩展后，一键导出 Cookie 为 JSON 格式")
    print()
    
    # 尝试从剪贴板读取（如果可用）
    try:
        import subprocess
        cookie = subprocess.check_output(['xclip', '-selection', 'clipboard', '-o'], 
                                        stderr=subprocess.DEVNULL).decode().strip()
        if cookie:
            print(f"✅ 检测到剪贴板中有内容（{len(cookie)} 字符）")
            use_clipboard = input("是否使用剪贴板中的 Cookie？(y/n): ")
            if use_clipboard.lower() == 'y':
                return cookie
    except:
        pass
    
    # 手动输入
    print("\n请粘贴 Cookie 字符串：")
    print("(粘贴后按回车，如果内容很长可以分多次粘贴，最后输入 'END' 结束)")
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)
    
    cookie = '\n'.join(lines)
    return cookie


def parse_cookie(cookie_str):
    """解析 Cookie 字符串为列表格式"""
    cookies = []
    
    # 如果是 JSON 格式
    if cookie_str.strip().startswith('['):
        try:
            return json.loads(cookie_str)
        except:
            pass
    
    # 如果是字符串格式
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.twitter.com',
                'path': '/'
            })
    
    return cookies


async def validate_cookies(scraper, cookies):
    """验证 Cookie 是否有效"""
    print("\n🔍 正在验证 Cookie...")
    
    try:
        # 加载 Cookie
        await scraper.page.context.add_cookies(cookies)
        
        # 访问 Twitter
        await scraper.page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        # 检查是否登录成功
        if await scraper.is_logged_in():
            print("✅ Cookie 验证成功！")
            return True
        else:
            print("❌ Cookie 无效或已过期")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败：{e}")
        return False


async def main():
    scraper = TwitterScraper(headless=True)
    
    try:
        await scraper.start()
        
        # 检查是否已有 Cookie 文件
        if os.path.exists("twitter_cookies.json"):
            print("✅ 检测到已有的 Cookie 文件")
            with open("twitter_cookies.json", 'r') as f:
                existing_cookies = json.load(f)
            
            # 验证现有 Cookie
            if await validate_cookies(scraper, existing_cookies):
                print("✅ 现有 Cookie 仍然有效，无需重新导入")
                return
            else:
                print("⚠️  现有 Cookie 已过期，需要重新导入")
        
        # 获取 Cookie
        cookie_str = get_cookie_from_user()
        
        if not cookie_str:
            print("❌ 未输入 Cookie")
            return
        
        # 解析 Cookie
        cookies = parse_cookie(cookie_str)
        
        if not cookies:
            print("❌ 无法解析 Cookie")
            return
        
        print(f"\n✅ 解析成功，共 {len(cookies)} 个 Cookie")
        
        # 验证 Cookie
        if await validate_cookies(scraper, cookies):
            # 保存 Cookie
            with open("twitter_cookies.json", 'w') as f:
                json.dump(cookies, f, indent=2)
            
            print("\n✅ Cookie 已保存到 twitter_cookies.json")
            print("\n🎉 现在可以运行工作流了:")
            print("   python3 main.py")
        else:
            print("\n❌ Cookie 无效，请重新获取")
            print("\n提示：")
            print("- 确保你已登录 Twitter")
            print("- Cookie 可能已过期，请重新复制")
            print("- 尝试使用浏览器扩展导出 Cookie")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
