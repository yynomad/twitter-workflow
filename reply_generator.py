"""
AI 回复生成模块（支持翻译）
支持多个 AI 服务提供商（阿里云百炼、火山引擎、DeepSeek 等）
"""

import os
from typing import List, Optional, Dict
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class ReplyOption:
    """回复选项"""
    content: str
    style: str
    translation: str = ""


class ReplyGenerator:
    """回复生成器"""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化回复生成器
        """
        # 加载 .env 文件
        from dotenv import load_dotenv
        load_dotenv()
        
        # 确定使用哪个提供商
        self.provider = provider or os.getenv("AI_PROVIDER", "volc")
        
        if self.provider == "bailian":
            self.api_key = api_key or os.getenv("BAILIAN_API_KEY")
            self.base_url = base_url or os.getenv("BAILIAN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            self.model = model or os.getenv("BAILIAN_MODEL", "qwen-plus")
            self.provider_name = "阿里云百炼"
        elif self.provider == "deepseek":
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.provider_name = "DeepSeek"
        elif self.provider == "volc":
            self.api_key = api_key or os.getenv("VOLC_API_KEY")
            self.base_url = base_url or os.getenv("VOLC_API_BASE", "https://ark.cn-beijing.volces.com/api/coding/v3")
            self.model = model or os.getenv("VOLC_MODEL", "DeepSeek-V3.2")
            self.provider_name = "火山方舟 Coding Plan"
        else:
            raise ValueError(f"不支持的 AI 提供商：{self.provider}")
        
        if not self.api_key:
            raise ValueError(f"{self.provider_name} API Key 未提供")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        print(f"✅ AI 服务：{self.provider_name} ({self.model})")

    def translate_tweet(self, tweet_text: str, target_language: str = "中文") -> str:
        """翻译推文"""
        system_prompt = f"""你是一个专业的翻译助手。请将以下内容翻译成{target_language}。

要求：
1. 保持原意不变
2. 语言自然流畅
3. 适合社交媒体语境
4. 只返回翻译结果"""

        user_prompt = f"请翻译：\n{tweet_text}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()

    def generate_replies(
        self,
        tweet_text: str,
        tweet_author: str,
        num_replies: int = 3,
        custom_instructions: Optional[str] = None,
        language: str = "中文",
        include_translation: bool = True
    ) -> Dict:
        """
        为推文生成回复（包含翻译）
        
        Returns:
            包含 original_tweet, translated_tweet, replies 的字典
        """
        import json
        
        # 翻译推文
        translation = None
        if include_translation and language == "中文":
            # 检测是否包含日文假名（平假名、片假名）- 这是日文的明确标识
            has_japanese = any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in tweet_text)
            # 检测是否包含中文字符
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in tweet_text)
            
            # 如果是日文，或不包含中文（即英文），则翻译
            if has_japanese or (not has_chinese and tweet_text.strip()):
                print("   正在翻译推文...")
                translation = self.translate_tweet(tweet_text, "中文")
        
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
        {{"content": "Reply content 1", "style": "风格描述 1", "translation": "中文翻译 1"}},
        {{"content": "Reply content 2", "style": "风格描述 2", "translation": "中文翻译 2"}},
        {{"content": "Reply content 3", "style": "风格描述 3", "translation": "中文翻译 3"}}
    ]
}}

注意：
- content 字段使用原文语言（通常是英文）
- translation 字段提供{language}翻译
- style 用{language}描述回复风格"""

        # 构建用户提示
        translation_note = f"\n推文翻译：{translation}" if translation else ""
        user_prompt = f"""请为以下推文生成{num_replies}条回复：

推文作者：@{tweet_author}
推文内容：
{tweet_text}{translation_note}

请生成不同风格的回复选项，每条回复都要包含原文和{language}翻译。"""

        # 调用 API
        print("   正在生成回复...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )
        
        # 解析响应
        content = response.choices[0].message.content.strip()
        
        # 提取 JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            data = json.loads(content)
            replies = []
            for r in data.get("replies", []):
                replies.append({
                    "content": r.get("content", ""),
                    "style": r.get("style", "通用"),
                    "translation": r.get("translation", "")
                })
            
            return {
                "original_tweet": tweet_text,
                "translated_tweet": translation,
                "replies": replies[:num_replies]
            }
        except json.JSONDecodeError:
            return {
                "original_tweet": tweet_text,
                "translated_tweet": translation,
                "replies": [
                    {"content": content, "style": "AI 生成", "translation": ""},
                ]
            }
