"""
AI 回复生成模块
使用火山引擎 API 为推文生成回复
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class ReplyOption:
    """回复选项"""
    content: str
    style: str  # 如：友好、专业、幽默


class ReplyGenerator:
    """回复生成器"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化回复生成器
        
        Args:
            api_key: 火山引擎 API Key，如果不传则从环境变量读取
            base_url: API 基础 URL，默认使用火山引擎
            model: 使用的模型名称，默认使用 Doubao-pro-4k
        """
        self.api_key = api_key or os.getenv("VOLC_API_KEY")
        if not self.api_key:
            raise ValueError("火山引擎 API Key 未提供，请设置 VOLC_API_KEY 环境变量")
        
        # 火山引擎 API 配置
        self.base_url = base_url or os.getenv(
            "VOLC_API_BASE",
            "https://ark.cn-beijing.volces.com/api/v3"
        )
        self.model = model or os.getenv("VOLC_MODEL", "doubao-pro-4k")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_replies(
        self,
        tweet_text: str,
        tweet_author: str,
        num_replies: int = 3,
        custom_instructions: Optional[str] = None,
        language: str = "中文"
    ) -> List[ReplyOption]:
        """
        为推文生成回复
        
        Args:
            tweet_text: 推文内容
            tweet_author: 推文作者
            num_replies: 生成回复数量
            custom_instructions: 自定义生成指令
            language: 回复语言
            
        Returns:
            ReplyOption 列表
        """
        # 构建系统提示
        system_prompt = f"""你是一个社交媒体助手，负责为 Twitter 推文生成自然、有吸引力的回复。

要求：
1. 回复要简洁，每条不超过 280 字符
2. 回复要自然，像真人写的
3. 生成{num_replies}条不同风格的回复
4. 使用{language}回复
5. 每条回复要有独特的视角和风格

{custom_instructions or ''}

请以 JSON 格式返回，格式如下：
{{
    "replies": [
        {{"content": "回复内容 1", "style": "风格描述 1"}},
        {{"content": "回复内容 2", "style": "风格描述 2"}},
        {{"content": "回复内容 3", "style": "风格描述 3"}}
    ]
}}"""

        # 构建用户提示
        user_prompt = f"""请为以下推文生成{num_replies}条回复：

推文作者：@{tweet_author}
推文内容：
{tweet_text}

请生成不同风格的回复选项。"""

        # 调用火山引擎 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        # 解析响应
        import json
        content = response.choices[0].message.content.strip()
        
        # 尝试提取 JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            data = json.loads(content)
            replies = []
            for r in data.get("replies", []):
                replies.append(ReplyOption(
                    content=r.get("content", ""),
                    style=r.get("style", "通用")
                ))
            return replies[:num_replies]
        except json.JSONDecodeError:
            # 如果解析失败，返回简化版本
            return [
                ReplyOption(content=content, style="AI 生成"),
            ]
    
    def generate_reply_variations(
        self,
        base_reply: str,
        num_variations: int = 2
    ) -> List[str]:
        """
        基于基础回复生成变体
        
        Args:
            base_reply: 基础回复内容
            num_variations: 变体数量
            
        Returns:
            变体回复列表
        """
        system_prompt = """你是一个文本改写助手。请基于给定的回复，生成几个意思相近但表达方式不同的变体。
保持原意不变，只改变表达方式。"""
        
        user_prompt = f"""基础回复：
{base_reply}

请生成{num_variations}个变体版本，保持原意但用不同的表达方式。"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        # 简单按行分割
        variations = [line.strip() for line in content.split('\n') if line.strip()]
        return variations[:num_variations]
