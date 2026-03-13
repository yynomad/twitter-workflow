#!/usr/bin/env python3
"""
阿里云百炼 API 测试

测试阿里云百炼（Bailian）API 是否可用
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_bailian():
    """测试阿里云百炼 API"""
    
    api_key = os.getenv("BAILIAN_API_KEY")
    base_url = os.getenv("BAILIAN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("BAILIAN_MODEL", "qwen-plus")
    
    print("=" * 70)
    print("阿里云百炼 API 测试")
    print("=" * 70)
    print(f"\n配置信息:")
    print(f"  API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"  Base URL: {base_url}")
    print(f"  模型：{model}")
    print()
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # 测试对话
    print("测试对话...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "你好，请用中文回复 OK"}
            ],
            max_tokens=20,
            timeout=30
        )
        print(f"  ✅ 成功！")
        print(f"  响应：{response.choices[0].message.content}")
        print(f"  Token 使用：{response.usage.total_tokens}")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ 失败：{error_msg[:100]}")
        
        if "401" in error_msg:
            print(f"\n  💡 API Key 无效，请检查:")
            print(f"     1. 访问 https://bailian.console.aliyun.com")
            print(f"     2. 获取正确的 API Key")
            print(f"     3. 更新 .env 文件中的 BAILIAN_API_KEY")
        elif "404" in error_msg:
            print(f"\n  💡 模型不存在或 Base URL 错误")
        elif "429" in error_msg:
            print(f"\n  💡 速率限制")
        
        return False


if __name__ == "__main__":
    success = test_bailian()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 测试通过！可以运行 main.py")
    else:
        print("❌ 测试失败，请检查配置")
        print("\n获取 API Key:")
        print("  1. 访问：https://bailian.console.aliyun.com")
        print("  2. 登录阿里云账号")
        print("  3. 进入 API 管理")
        print("  4. 创建或复制 API Key")
        print("  5. 更新 .env 文件")
