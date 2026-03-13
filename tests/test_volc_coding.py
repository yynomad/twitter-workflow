#!/usr/bin/env python3
"""
火山方舟 Coding Plan API 测试 - 最简单版本

Base URL: https://ark.cn-beijing.volces.com/api/coding/v3
(兼容 OpenAI 接口协议)

用法：python3 test_volc_coding.py
"""

from openai import OpenAI

# 配置 - Coding Plan 专用
API_KEY = "YOUR-VOLC-API-KEY-HERE"
BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"  # Coding Plan 专用

print("=" * 60)
print("火山方舟 Coding Plan API 测试")
print("=" * 60)
print()
print(f"Base URL: {BASE_URL}")
print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print()

# 创建客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# 测试：调用模型
print("测试模型调用...")
print("输入：hello")
print()

try:
    response = client.chat.completions.create(
        model="DeepSeek-V3.2",  # Coding Plan 模型
        messages=[
            {"role": "user", "content": "hello"}
        ],
        max_tokens=50,
        timeout=30
    )
    print("✅ 成功！")
    print(f"模型回复：{response.choices[0].message.content}")
    print(f"Token 使用：{response.usage.total_tokens}")
except Exception as e:
    error_msg = str(e)
    print(f"❌ 失败：{error_msg[:100]}")
    
    if "404" in error_msg:
        print("\n💡 模型未开通，请在控制台开通 DeepSeek-V3.2")
        print("   https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement")
    elif "401" in error_msg:
        print("\n💡 API Key 无效")
    elif "429" in error_msg:
        print("\n💡 速率限制")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
