"""
Twitter 推文爬虫 - Playwright 浏览器自动化
"""

import asyncio
import json
import os
from typing import List
from dataclasses import dataclass
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
    view_count: int
    url: str


class TwitterScraper:
    """Twitter 爬虫"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
    
    async def start(self, cookie_file: str = "twitter_cookies.json"):
        """启动浏览器并加载 Cookie"""
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
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
        """保存 Cookie"""
        if self.context:
            cookies = await self.context.cookies()
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✅ Cookie 已保存：{cookie_file}")
    
    async def is_logged_in(self) -> bool:
        """检查是否已登录"""
        if not self.page:
            return False
        
        await self.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        current_url = self.page.url
        return "login" not in current_url and "i/flow/login" not in current_url
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        min_likes: int = 0,
        min_retweets: int = 0,
        min_views: int = 0,
        max_replies: int = 999999
    ) -> List[Tweet]:
        """搜索推文"""
        if not self.page:
            await self.start()
        
        import urllib.parse
        search_query = f"{query} -filter:replies -filter:retweets"
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"https://twitter.com/search?q={encoded_query}&f=live"
        print(f"🔍 搜索：{search_query}")
        print(f"   最小点赞：{min_likes}, 最小浏览：{min_views}, 最大评论：{max_replies}")
        
        await self.page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # 滚动加载
        for _ in range(5):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
        
        tweets = await self._extract_tweets(min_likes, min_retweets, min_views, max_replies)
        print(f"✅ 找到 {len(tweets)} 条推文")
        return tweets[:max_results]
    
    async def _extract_tweets(
        self,
        min_likes: int = 0,
        min_retweets: int = 0,
        min_views: int = 0,
        max_replies: int = 999999
    ) -> List[Tweet]:
        """提取推文"""
        tweets = []
        articles = self.page.locator('article[data-testid="tweet"]')
        count = await articles.count()
        
        for i in range(count):
            try:
                article = articles.nth(i)
                
                # 文本
                text_elem = article.locator('div[data-testid="tweetText"]')
                if await text_elem.count() == 0:
                    continue
                text = await text_elem.first.inner_text()
                
                # 作者
                user_elem = article.locator('a[href^="/"][href*="/status"]').first
                if await user_elem.count() == 0:
                    continue
                href = await user_elem.get_attribute('href')
                username = href.split('/')[1] if href else 'unknown'
                
                # 互动数据
                like_count = 0
                retweet_count = 0
                reply_count = 0
                view_count = 0
                
                like_elem = article.locator('div[data-testid="like"]')
                if await like_elem.count() > 0:
                    like_count = self._parse_count(await like_elem.first.inner_text())
                
                retweet_elem = article.locator('div[data-testid="retweet"]')
                if await retweet_elem.count() > 0:
                    retweet_count = self._parse_count(await retweet_elem.first.inner_text())
                
                reply_elem = article.locator('div[data-testid="reply"]')
                if await reply_elem.count() > 0:
                    reply_count = self._parse_count(await reply_elem.first.inner_text())
                
                # 浏览数（Twitter 显示为 "1.5K views" 或 "1.5M views"）
                # 尝试多种选择器
                view_count = 0
                for selector in [
                    'div[data-testid="analytics"]',
                    'span:has-text("views")',
                    'span:has-text("回表示")',
                ]:
                    view_elem = article.locator(selector)
                    if await view_elem.count() > 0:
                        view_text = await view_elem.first.inner_text()
                        view_count = self._parse_count(view_text)
                        if view_count > 0:
                            break
                
                # 过滤条件
                if like_count < min_likes or retweet_count < min_retweets:
                    continue
                if view_count < min_views:
                    continue
                if reply_count > max_replies:
                    continue
                
                # 链接和 ID
                status_links = article.locator('a[href*="/status/"]')
                status_url = ""
                tweet_id = ""
                for j in range(await status_links.count()):
                    link = await status_links.nth(j).get_attribute('href')
                    if '/status/' in link:
                        status_url = f"https://twitter.com{link}"
                        tweet_id = link.split('/status/')[-1].split('?')[0]
                        break
                
                if not tweet_id:
                    continue
                
                # 作者名
                name_elem = article.locator('div[data-testid="User-Name"] span')
                author_name = await name_elem.first.inner_text() if await name_elem.count() > 0 else ""
                
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
                    view_count=view_count,
                    url=status_url
                ))
                
            except Exception as e:
                print(f"⚠️  提取失败：{e}")
                continue
        
        return tweets
    
    def _parse_count(self, text: str) -> int:
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
