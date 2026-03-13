#!/usr/bin/env python3
"""
火山方舟 API 测试 - 最简单版本

用法：python3 test_volc_simple.py
"""

from openai import OpenAI

# 配置
API_KEY = "YOUR-VOLC-API-KEY-HERE"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

print("=" * 60)
print("火山方舟 API 测试")
print("=" * 60)
print()

# 创建客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# 测试 1：获取可用模型列表
print("1. 获取可用模型列表...")
try:
    models = client.models.list()
    print(f"   ✅ 找到 {len(models.data)} 个模型")
    
    # 显示前 5 个
    print("   前 5 个模型:")
    for i, model in enumerate(models.data[:5], 1):
        print(f"      {i}. {model.id}")
except Exception as e:
    print(f"   ❌ 失败：{e}")

print()

# 测试 2：调用模型
print("2. 调用模型测试...")
print("   输入：hello")

# 尝试不同的模型
models_to_try = [
    "DeepSeek-V3.2",
    "deepseek-v3-2-251201",
    "doubao-pro-4k-240515",
    "doubao-lite-4k-240328"
]

for model_name in models_to_try:
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "hello"}
            ],
            max_tokens=50
        )
        print(f"   ✅ 模型 {model_name} 可用！")
        print(f"   回复：{response.choices[0].message.content}")
        print(f"   Token 使用：{response.usage.total_tokens}")
        break
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"   ❌ {model_name}: 模型不存在或未开通")
        elif "401" in error_msg:
            print(f"   ❌ {model_name}: API Key 无效")
            break
        else:
            print(f"   ❌ {model_name}: {error_msg[:50]}")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
