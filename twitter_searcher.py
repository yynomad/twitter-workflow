"""
Twitter 推文查询模块
使用 Twitter API v2 查询符合条件的推文
"""

import tweepy
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


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


class TwitterSearcher:
    """Twitter 推文搜索器"""
    
    def __init__(self, bearer_token: str):
        """
        初始化 Twitter 搜索器
        
        Args:
            bearer_token: Twitter API Bearer Token
        """
        self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    
    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        recent_only: bool = True,
        min_likes: int = 0,
        min_retweets: int = 0,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> List[Tweet]:
        """
        搜索符合条件的推文
        
        Args:
            query: 搜索查询语句（支持 Twitter 高级搜索语法）
            max_results: 最大返回结果数
            recent_only: 是否只搜索最近 7 天的推文
            min_likes: 最小点赞数
            min_retweets: 最小转发数
            exclude_replies: 是否排除回复
            exclude_retweets: 是否排除转推
            
        Returns:
            Tweet 对象列表
        """
        # 构建查询语句
        search_query = query
        
        # 添加过滤条件
        if exclude_replies:
            search_query += " -is:reply"
        if exclude_retweets:
            search_query += " -is:retweet"
        if min_likes > 0:
            search_query += f" min_faves:{min_likes}"
        if min_retweets > 0:
            search_query += f" min_retweets:{min_retweets}"
        
        # 设置时间范围
        start_time = None
        if recent_only:
            start_time = datetime.utcnow() - timedelta(days=7)
        
        # 执行搜索
        tweets = self.client.search_recent_tweets(
            query=search_query,
            max_results=min(max_results, 100),  # API 限制每次最多 100 条
            start_time=start_time,
            tweet_fields=['created_at', 'author_id', 'public_metrics', 'conversation_id'],
            expansions=['author_id'],
            user_fields=['username', 'name']
        )
        
        if not tweets.data:
            return []
        
        # 构建用户映射
        users = {u.id: u for u in (tweets.includes.get('users', []) or [])}
        
        # 转换为 Tweet 对象
        result = []
        for tweet in tweets.data:
            author = users.get(tweet.author_id, {})
            result.append(Tweet(
                id=tweet.id,
                text=tweet.text,
                author_id=tweet.author_id,
                author_username=author.get('username', 'unknown'),
                author_name=author.get('name', 'Unknown'),
                created_at=tweet.created_at.isoformat() if tweet.created_at else '',
                like_count=tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                retweet_count=tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                reply_count=tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                url=f"https://twitter.com/{author.get('username', 'unknown')}/status/{tweet.id}"
            ))
        
        return result
    
    def get_user_timeline(
        self,
        username: str,
        max_results: int = 10,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> List[Tweet]:
        """
        获取指定用户的最新推文
        
        Args:
            username: Twitter 用户名（不带@）
            max_results: 最大返回结果数
            exclude_replies: 是否排除回复
            exclude_retweets: 是否排除转推
            
        Returns:
            Tweet 对象列表
        """
        # 获取用户 ID
        user = self.client.get_user(username=username, user_fields=['id'])
        if not user.data:
            return []
        
        user_id = user.data.id
        
        # 获取用户推文
        tweets = self.client.get_users_tweets(
            id=user_id,
            max_results=min(max_results, 100),
            exclude=['replies'] if exclude_replies else None,
            tweet_fields=['created_at', 'public_metrics'],
        )
        
        if not tweets.data:
            return []
        
        # 转换为 Tweet 对象
        result = []
        for tweet in tweets.data:
            if exclude_retweets and tweet.text.startswith('RT @'):
                continue
            result.append(Tweet(
                id=tweet.id,
                text=tweet.text,
                author_id=user_id,
                author_username=username,
                author_name=user.data.name if user.data else username,
                created_at=tweet.created_at.isoformat() if tweet.created_at else '',
                like_count=tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                retweet_count=tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                reply_count=tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                url=f"https://twitter.com/{username}/status/{tweet.id}"
            ))
        
        return result
