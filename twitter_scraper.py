"""
Twitter 推文搜索模块 - Playwright 浏览器自动化版本
无需 Twitter API，直接通过浏览器抓取搜索结果
"""

import asyncio
import re
import json
import os
from typing import List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


@dataclass
class Tweet:
    """推文数据类"""
    id: str
    text: str
    author_id: str
    author_username: str
    author_name: str
    created_at: str
    like_count: int
    retweet_count: int
    reply_count: int
    url: str


class TwitterScraper:
    """Twitter 爬虫（基于 Playwright）"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式（不显示浏览器窗口）
            timeout: 页面加载超时时间（毫秒）
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start(self, cookie_file: str = "twitter_cookies.json"):
        """
        启动浏览器并加载 Cookie
        
        Args:
            cookie_file: Cookie 保存文件路径
        """
        playwright = await async_playwright().start()
        
        # 启动浏览器
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 加载 Cookie
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            await self.context.add_cookies(cookies)
            print(f"✅ 已加载 Cookie: {cookie_file}")
        
        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.timeout)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
    async def save_cookies(self, cookie_file: str = "twitter_cookies.json"):
        """保存 Cookie 到文件"""
        if self.context:
            cookies = await self.context.cookies()
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✅ Cookie 已保存：{cookie_file}")
    
    async def login(self):
        """
        手动登录 Twitter
        
        使用方法：
        1. 运行此方法会打开浏览器
        2. 手动登录 Twitter
        3. 登录后按回车键保存 Cookie
        """
        if not self.page:
            await self.start()
        
        print("\n📱 请在浏览器中登录 Twitter...")
        print("   登录后按回车键保存 Cookie\n")
        
        await self.page.goto("https://twitter.com/login", wait_until="domcontentloaded")
        
        # 等待用户登录（检测是否跳转到首页）
        try:
            await self.page.wait_for_url("https://twitter.com/home", timeout=120000)
            print("✅ 检测到登录成功")
        except:
            print("⚠️  等待登录超时，但继续尝试...")
        
        input("按回车键保存 Cookie...")
        await self.save_cookies()
        print("✅ Cookie 已保存，下次无需手动登录")
    
    async def is_logged_in(self) -> bool:
        """检查是否已登录"""
        if not self.page:
            return False
        
        await self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # 检查是否被重定向到登录页
        current_url = self.page.url
        if "login" in current_url or "i/flow/login" in current_url:
            return False
        
        return True
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        min_likes: int = 0,
        min_retweets: int = 0,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> List[Tweet]:
        """
        搜索推文
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            min_likes: 最小点赞数
            min_retweets: 最小转发数
            exclude_replies: 排除回复
            exclude_retweets: 排除转推
            
        Returns:
            Tweet 列表
        """
        if not self.page:
            await self.start()
        
        # 构建搜索 URL
        search_query = query
        if exclude_replies:
            search_query += " -filter:replies"
        if exclude_retweets:
            search_query += " -filter:retweets"
        
        # URL 编码
        import urllib.parse
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://twitter.com/search?q={encoded_query}&f=live"
        print(f"🔍 搜索：{search_query}")
        
        await self.page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)  # 等待页面加载
        
        # 滚动页面加载更多结果
        await self._scroll_and_load(max_results)
        
        # 提取推文
        tweets = await self._extract_tweets(min_likes, min_retweets)
        
        print(f"✅ 找到 {len(tweets)} 条推文")
        return tweets[:max_results]
    
    async def _scroll_and_load(self, max_results: int):
        """滚动页面加载更多推文"""
        scroll_times = max(3, max_results // 5)  # 每次滚动约加载 5 条
        
        for i in range(scroll_times):
            # 滚动到底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)  # 等待加载
            
            # 检查是否还有更多内容
            try:
                # 检测"显示更多"按钮
                show_more = self.page.locator('div[role="button"]:has-text("Show more")')
                if await show_more.count() > 0:
                    await show_more.first.click()
                    await asyncio.sleep(2)
            except:
                pass
    
    async def _extract_tweets(self, min_likes: int, min_retweets: int) -> List[Tweet]:
        """从页面提取推文"""
        tweets = []
        
        # 查找所有推文文章
        articles = self.page.locator('article[data-testid="tweet"]')
        count = await articles.count()
        
        for i in range(count):
            try:
                article = articles.nth(i)
                
                # 提取推文文本
                text_elem = article.locator('div[data-testid="tweetText"]')
                if await text_elem.count() == 0:
                    continue
                text = await text_elem.first.inner_text()
                
                # 提取作者信息
                user_elem = article.locator('a[href^="/"][href*="/status"]').first
                if await user_elem.count() == 0:
                    continue
                
                # 获取作者用户名（从 href 中提取）
                href = await user_elem.get_attribute('href')
                username = href.split('/')[1] if href else 'unknown'
                
                # 提取互动数据
                like_count = 0
                retweet_count = 0
                reply_count = 0
                
                # 点赞数
                like_elem = article.locator('div[data-testid="like"]')
                if await like_elem.count() > 0:
                    like_text = await like_elem.first.inner_text()
                    like_count = self._parse_count(like_text)
                
                # 转发数
                retweet_elem = article.locator('div[data-testid="retweet"]')
                if await retweet_elem.count() > 0:
                    retweet_text = await retweet_elem.first.inner_text()
                    retweet_count = self._parse_count(retweet_text)
                
                # 回复数
                reply_elem = article.locator('div[data-testid="reply"]')
                if await reply_elem.count() > 0:
                    reply_text = await reply_elem.first.inner_text()
                    reply_count = self._parse_count(reply_text)
                
                # 过滤条件
                if like_count < min_likes or retweet_count < min_retweets:
                    continue
                
                # 提取推文 ID 和链接
                status_links = article.locator('a[href*="/status/"]')
                status_url = ""
                tweet_id = ""
                if await status_links.count() > 0:
                    # 找第一个状态链接（通常是时间戳链接）
                    for j in range(await status_links.count()):
                        link = await status_links.nth(j).get_attribute('href')
                        if '/status/' in link:
                            status_url = f"https://twitter.com{link}"
                            tweet_id = link.split('/status/')[-1].split('?')[0]
                            break
                
                if not tweet_id:
                    continue
                
                # 提取作者名称
                name_elem = article.locator('div[data-testid="User-Name"] span')
                author_name = ""
                if await name_elem.count() > 0:
                    author_name = await name_elem.first.inner_text()
                
                tweets.append(Tweet(
                    id=tweet_id,
                    text=text,
                    author_id=username,
                    author_username=username,
                    author_name=author_name,
                    created_at=datetime.now().isoformat(),
                    like_count=like_count,
                    retweet_count=retweet_count,
                    reply_count=reply_count,
                    url=status_url
                ))
                
            except Exception as e:
                print(f"⚠️  提取第 {i} 条推文失败：{e}")
                continue
        
        return tweets
    
    def _parse_count(self, text: str) -> int:
        """解析数字（处理 1.5K, 2M 等格式）"""
        if not text:
            return 0
        
        text = text.strip()
        
        # 移除逗号
        text = text.replace(',', '')
        
        # 处理 K, M 等单位
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, mult in multipliers.items():
            if suffix in text.upper():
                num_str = text.upper().replace(suffix, '')
                try:
                    return int(float(num_str) * mult)
                except:
                    return 0
        
        try:
            return int(text)
        except:
            return 0


async def main():
    """测试脚本"""
    scraper = TwitterScraper(headless=False)  # 显示浏览器方便调试
    
    try:
        await scraper.start()
        
        # 检查是否已登录
        if not await scraper.is_logged_in():
            print("❌ 未登录，请先登录 Twitter")
            await scraper.login()
        
        # 搜索推文
        tweets = await scraper.search_tweets(
            query="AI",
            max_results=5,
            min_likes=10
        )
        
        print(f"\n📊 搜索结果：")
        for tweet in tweets:
            print(f"\n- @{tweet.author_username}: {tweet.text[:50]}...")
            print(f"  👍 {tweet.like_count} | 🔄 {tweet.retweet_count}")
            print(f"  🔗 {tweet.url}")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
