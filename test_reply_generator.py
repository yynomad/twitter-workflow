#!/usr/bin/env python3
"""
AI 回复生成器测试
测试 AI 生成回复功能
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

from reply_generator import ReplyGenerator


def test_generate_replies():
    """测试生成回复"""
    print("=" * 60)
    print("🧪 测试：AI 生成回复")
    print("=" * 60)
    
    # 检查 API Key
    if not os.getenv("VOLC_API_KEY"):
        print("❌ 失败：VOLC_API_KEY 未设置")
        print("   请检查 .env 文件")
        return False
    
    print("\n1️⃣ 初始化回复生成器...")
    try:
        generator = ReplyGenerator()
        print("   ✅ 初始化成功")
    except Exception as e:
        print(f"   ❌ 初始化失败：{e}")
        return False
    
    # 测试用例
    test_cases = [
        {
            "name": "英文推文",
            "text": "Just launched our new AI product! Excited to see what users think. #AI #ProductLaunch",
            "author": "techfounder"
        },
        {
            "name": "日文推文",
            "text": "新しい AI 機能をリリースしました！皆さんに使ってみてもらえて嬉しいです。",
            "author": "tokyo_dev"
        },
        {
            "name": "中文推文",
            "text": "今天分享一个超好用的 AI 工具，效率提升 10 倍！#AI #效率工具",
            "author": "productivity_guru"
        }
    ]
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ 测试：{case['name']}")
        print(f"   作者：@{case['author']}")
        print(f"   内容：{case['text'][:50]}...")
        
        try:
            result = generator.generate_replies(
                tweet_text=case["text"],
                tweet_author=case["author"],
                num_replies=3,
                custom_instructions="回复要友好、有建设性",
                language="中文"
            )
            
            print(f"   ✅ 生成 {len(result['replies'])} 条回复")
            
            # 检查翻译
            if result.get('translated_tweet'):
                print(f"   📝 翻译：{result['translated_tweet'][:50]}...")
            
            # 显示第一条回复
            if result['replies']:
                first = result['replies'][0]
                print(f"   💬 回复示例 [{first['style']}]:")
                print(f"      {first['content'][:80]}...")
                if first.get('translation'):
                    print(f"      翻译：{first['translation'][:50]}...")
            
            # 验证结果
            if len(result['replies']) >= 2:
                results.append(True)
            else:
                print("   ⚠️  回复数量不足")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ 生成失败：{e}")
            results.append(False)
    
    return all(results)


def test_translation_detection():
    """测试语言检测和翻译逻辑"""
    print("\n" + "=" * 60)
    print("🧪 测试：语言检测")
    print("=" * 60)
    
    test_cases = [
        ("Hello world", False, "英文"),
        ("こんにちは", True, "日文（平假名）"),
        ("こんにちは", True, "日文（片假名）"),
        ("你好世界", False, "中文"),
        ("AI とは", True, "日文混合"),
    ]
    
    results = []
    
    for text, expected_japanese, desc in test_cases:
        has_japanese = any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
        
        # 应该翻译的情况：有日文，或者没有中文
        should_translate = has_japanese or (not has_chinese and text.strip())
        
        status = "✅" if (has_japanese == expected_japanese) else "⚠️"
        print(f"{status} {desc}: 日文={has_japanese}, 中文={has_chinese}, 应翻译={should_translate}")
        results.append(has_japanese == expected_japanese)
    
    return all(results)


def test_custom_instructions():
    """测试自定义指令"""
    print("\n" + "=" * 60)
    print("🧪 测试：自定义指令")
    print("=" * 60)
    
    if not os.getenv("VOLC_API_KEY"):
        print("⚠️  跳过：VOLC_API_KEY 未设置")
        return True
    
    generator = ReplyGenerator()
    
    custom_instruction = "回复要非常简短，不超过 20 个字"
    
    print(f"\n指令：{custom_instruction}")
    
    try:
        result = generator.generate_replies(
            tweet_text="AI is changing the world!",
            tweet_author="ai_enthusiast",
            num_replies=2,
            custom_instructions=custom_instruction,
            language="中文"
        )
        
        print(f"✅ 生成 {len(result['replies'])} 条回复")
        
        for i, reply in enumerate(result['replies'], 1):
            content = reply['content']
            translation = reply.get('translation', '')
            print(f"\n   [{i}] {content}")
            print(f"       {translation}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("\n🚀 AI 回复生成器测试套件\n")
    
    results = []
    
    # 测试 1: 生成回复
    results.append(test_generate_replies())
    
    # 测试 2: 语言检测
    results.append(test_translation_detection())
    
    # 测试 3: 自定义指令
    results.append(test_custom_instructions())
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过：{passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
