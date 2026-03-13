#!/usr/bin/env python3
"""
火山方舟 API 测试用例

测试火山方舟 DeepSeek-V3.2 模型是否可用
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 配置
load_dotenv()

def test_volc_model():
    """测试火山方舟模型"""
    
    # 获取配置
    api_key = os.getenv("VOLC_API_KEY")
    base_url = os.getenv("VOLC_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
    model = os.getenv("VOLC_MODEL", "deepseek-v3-2-251201")
    
    print("=" * 70)
    print("火山方舟 API 测试")
    print("=" * 70)
    print(f"\n配置信息:")
    print(f"  API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"  Base URL: {base_url}")
    print(f"  模型：{model}")
    print()
    
    # 创建客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    # 测试 1：简单对话
    print("测试 1: 简单对话...")
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
        
        # 分析错误
        if "404" in error_msg:
            if "ModelNotOpen" in error_msg:
                print(f"\n  💡 模型未开通，请在控制台开通：https://console.volcengine.com/ark")
            else:
                print(f"\n  💡 模型不存在或无权限")
        elif "401" in error_msg:
            print(f"\n  💡 API Key 无效")
        elif "429" in error_msg:
            print(f"\n  💡 速率限制")
        
        return False


def test_twitter_workflow():
    """测试完整的 Twitter 工作流"""
    
    print("\n" + "=" * 70)
    print("Twitter Workflow 完整测试")
    print("=" * 70)
    
    # 检查配置
    required_vars = [
        "VOLC_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    print("\n检查配置...")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已配置")
        else:
            print(f"  ❌ {var}: 未配置")
            return False
    
    # 测试 AI 生成
    print("\n测试 AI 回复生成...")
    try:
        from reply_generator import ReplyGenerator
        
        generator = ReplyGenerator(provider="volc")
        
        replies = generator.generate_replies(
            tweet_text="Just launched my new AI project!",
            tweet_author="testuser",
            num_replies=3,
            language="中文"
        )
        
        print(f"  ✅ 成功生成 {len(replies)} 条回复:")
        for i, reply in enumerate(replies, 1):
            print(f"    {i}. [{reply.style}] {reply.content[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 失败：{str(e)[:100]}")
        return False


def main():
    """主测试函数"""
    
    print("\n🚀 开始测试火山方舟 Twitter Workflow\n")
    
    # 测试 1：基础 API
    test1_passed = test_volc_model()
    
    # 测试 2：完整工作流
    test2_passed = test_twitter_workflow()
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"  基础 API 测试：{'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"  完整工作流测试：{'✅ 通过' if test2_passed else '❌ 失败'}")
    print()
    
    if test1_passed and test2_passed:
        print("🎉 所有测试通过！可以运行 main.py 了")
        print("\n运行命令:")
        print("  python3 main.py")
    else:
        print("⚠️  部分测试失败，请检查配置")
        print("\n解决步骤:")
        print("  1. 访问 https://console.volcengine.com/ark")
        print("  2. 开通 DeepSeek-V3.2 模型")
        print("  3. 重新运行测试")
    
    print()


if __name__ == "__main__":
    main()
