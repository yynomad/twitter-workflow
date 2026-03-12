#!/usr/bin/env python3
"""
火山引擎 API 测试工具

测试不同的模型配置，找到可用的模型
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 火山引擎配置
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 常见模型列表
AVAILABLE_MODELS = [
    # Doubao 系列
    "doubao-lite-4k-240515",
    "doubao-lite-32k-240515",
    "doubao-pro-4k-240515",
    "doubao-pro-32k-240515",
    "doubao-pro-128k-240515",
    # Doubao 1.5 系列
    "doubao-1-5-lite-32k-250115",
    "doubao-1-5-pro-32k-250115",
    # 其他可能可用的模型
    "ep-20240609164828-sjcjg",
    "ep-20241203150328-wmz8n",
]


def test_model(api_key: str, base_url: str, model: str) -> Dict:
    """
    测试单个模型是否可用
    
    Returns:
        测试结果字典
    """
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 发送测试请求
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, please respond with just 'OK'"}
            ],
            max_tokens=10,
            timeout=10
        )
        
        # 检查响应
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            return {
                "model": model,
                "status": "✅ 可用",
                "response": content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
            }
        else:
            return {
                "model": model,
                "status": "❌ 无响应",
                "error": "Empty response"
            }
            
    except Exception as e:
        error_msg = str(e)
        
        # 解析错误信息
        if "404" in error_msg:
            status = "❌ 模型不存在或无权限"
        elif "401" in error_msg:
            status = "❌ API Key 无效"
        elif "429" in error_msg:
            status = "⚠️  速率限制"
        elif "500" in error_msg:
            status = "⚠️  服务器错误"
        else:
            status = f"❌ 错误：{error_msg[:50]}"
        
        return {
            "model": model,
            "status": status,
            "error": error_msg
        }


def test_all_models():
    """测试所有可用模型"""
    
    # 获取配置
    api_key = os.getenv("VOLC_API_KEY")
    base_url = os.getenv("VOLC_API_BASE", DEFAULT_BASE_URL)
    
    if not api_key:
        print("❌ 错误：VOLC_API_KEY 未设置")
        print("   请在 .env 文件中配置 VOLC_API_KEY")
        sys.exit(1)
    
    print("=" * 70)
    print("火山引擎 API 模型测试工具")
    print("=" * 70)
    print(f"\nAPI Base: {base_url}")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"测试模型数量：{len(AVAILABLE_MODELS)}\n")
    
    results = []
    
    # 测试每个模型
    for i, model in enumerate(AVAILABLE_MODELS, 1):
        print(f"[{i}/{len(AVAILABLE_MODELS)}] 测试模型：{model}...", end=" ")
        sys.stdout.flush()
        
        result = test_model(api_key, base_url, model)
        results.append(result)
        
        print(f"{result['status']}")
        
        if "✅" in result["status"]:
            print(f"       响应：{result.get('response', 'N/A')}")
            print(f"       Token: {result.get('usage', {})}")
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    available = [r for r in results if "✅" in r["status"]]
    unavailable = [r for r in results if "❌" in r["status"] or "⚠️" in r["status"]]
    
    if available:
        print(f"\n✅ 可用模型 ({len(available)} 个):")
        for r in available:
            print(f"   - {r['model']}")
        
        # 推荐第一个可用的模型
        print(f"\n💡 推荐配置:")
        print(f"   VOLC_MODEL={available[0]['model']}")
    else:
        print(f"\n❌ 没有可用的模型")
    
    if unavailable:
        print(f"\n⚠️  不可用模型 ({len(unavailable)} 个):")
        for r in unavailable:
            print(f"   - {r['model']}: {r['status']}")
    
    print("\n" + "=" * 70)
    
    # 保存推荐配置
    if available:
        recommend_model = available[0]["model"]
        print(f"\n📝 正在更新 .env 文件...")
        
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 更新或添加 VOLC_MODEL
            if "VOLC_MODEL=" in content:
                content = content.replace(
                    f'VOLC_MODEL={content.split("VOLC_MODEL=")[1].split(chr(10))[0]}',
                    f'VOLC_MODEL={recommend_model}'
                )
            else:
                content += f"\nVOLC_MODEL={recommend_model}\n"
            
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"✅ 已更新 .env 文件，推荐模型：{recommend_model}")
        else:
            print(f"⚠️  未找到 .env 文件，请手动配置 VOLC_MODEL={recommend_model}")


def test_custom_model(model: str):
    """测试自定义模型"""
    api_key = os.getenv("VOLC_API_KEY")
    base_url = os.getenv("VOLC_API_BASE", DEFAULT_BASE_URL)
    
    if not api_key:
        print("❌ 错误：VOLC_API_KEY 未设置")
        sys.exit(1)
    
    print(f"测试自定义模型：{model}")
    print("-" * 70)
    
    result = test_model(api_key, base_url, model)
    
    print(f"模型：{result['model']}")
    print(f"状态：{result['status']}")
    
    if "✅" in result["status"]:
        print(f"响应：{result.get('response', 'N/A')}")
        print(f"Token 使用：{result.get('usage', {})}")
    else:
        print(f"错误：{result.get('error', 'Unknown')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="火山引擎 API 模型测试工具")
    parser.add_argument(
        "-m", "--model",
        type=str,
        help="测试指定模型（不填则测试所有预定义模型）"
    )
    
    args = parser.parse_args()
    
    if args.model:
        test_custom_model(args.model)
    else:
        test_all_models()
