#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate multi-selection test cases for libpinyin
Simulates real user behavior: selecting candidates multiple times to build complete sentence
"""

import json

def generate_multi_selection_tests():
    """
    Generate test cases where users make multiple selections
    Format: Each test has a list of selections, each with expected phrase
    """
    
    test_cases = []
    test_id = 1
    
    # Category 1: Two-step selections (common pattern)
    two_step_tests = [
        {
            "prefix": "",
            "pinyin": "zhongguorenminyinggai",
            "description": "Two-step: 中国人民 → 应该",
            "selections": [
                {"index": 0, "expected_contains": "中国人民"},
                {"index": 0, "expected_contains": "应该"}
            ],
            "final_sentence": "中国人民应该"
        },
        {
            "prefix": "我认为",
            "pinyin": "zhongguorenminyinggaigengjianulideweixiandaihuaerfendou",
            "description": "Two-step with prefix: 中国人民 → full sentence",
            "selections": [
                {"index": 0, "expected_contains": "中国人民"},
                {"index": 0, "expected_contains": "中国人民应该更加努力的为现代化而奋斗"}
            ],
            "final_sentence": "中国人民应该更加努力的为现代化而奋斗"
        },
        {
            "prefix": "",
            "pinyin": "jintiantianqihenhao",
            "description": "Two-step: 今天 → 天气很好",
            "selections": [
                {"index": 0, "expected_contains": "今天"},
                {"index": 0, "expected_contains": "天气"}
            ],
            "final_sentence": "今天天气很好"
        },
        {
            "prefix": "",
            "pinyin": "womenyiqiquwanr",
            "description": "Two-step: 我们 → 一起去玩",
            "selections": [
                {"index": 0, "expected_contains": "我们"},
                {"index": 0, "expected_contains": "一起"}
            ],
            "final_sentence": "我们一起去玩"
        },
    ]
    
    # Category 2: Three-step selections (building longer sentences)
    three_step_tests = [
        {
            "prefix": "",
            "pinyin": "jintiantianqihenhaowomenyiqiquwanr",
            "description": "Three-step: 今天 → 天气 → 很好我们一起去玩",
            "selections": [
                {"index": 0, "expected_contains": "今天"},
                {"index": 0, "expected_contains": "天气"},
                {"index": 0, "expected_contains": "很好"}
            ],
            "final_sentence": "今天天气很好我们一起去玩"
        },
        {
            "prefix": "",
            "pinyin": "tazuotianmailehenduodongxi",
            "description": "Three-step: 他 → 昨天 → 买了很多东西",
            "selections": [
                {"index": 0, "expected_contains": "他"},
                {"index": 0, "expected_contains": "昨天"},
                {"index": 0, "expected_contains": "买了"}
            ],
            "final_sentence": "他昨天买了很多东西"
        },
        {
            "prefix": "我觉得",
            "pinyin": "zhegebanfafeichagghao",
            "description": "Three-step with prefix: 这个 → 办法 → 非常好",
            "selections": [
                {"index": 0, "expected_contains": "这个"},
                {"index": 0, "expected_contains": "办法"},
                {"index": 0, "expected_contains": "非常"}
            ],
            "final_sentence": "这个办法非常好"
        },
    ]
    
    # Category 3: Multiple selections with corrections (non-zero index)
    correction_tests = [
        {
            "prefix": "",
            "pinyin": "wohengaoxing",
            "description": "Correction: select index 2 for correct '很'",
            "selections": [
                {"index": 0, "expected_contains": "我"},
                {"index": 2, "expected_contains": "很"}  # Not first choice
            ],
            "final_sentence": "我很高兴",
            "note": "Tests selecting non-first candidate"
        },
        {
            "prefix": "我是",
            "pinyin": "nidaye",
            "description": "Correction: select index 1 for '大爷'",
            "selections": [
                {"index": 0, "expected_contains": "你"},
                {"index": 1, "expected_contains": "大"}  # Second choice
            ],
            "final_sentence": "你大爷",
            "note": "Tests homophone resolution"
        },
    ]
    
    # Category 4: Long sentence with multiple steps
    long_multi_tests = [
        {
            "prefix": "我看",
            "pinyin": "zhegewentiyijingdedaolejiejue",
            "description": "Long multi-step: 这个 → 问题 → 已经得到了解决",
            "selections": [
                {"index": 0, "expected_contains": "这个"},
                {"index": 0, "expected_contains": "问题"},
                {"index": 0, "expected_contains": "已经"}
            ],
            "final_sentence": "这个问题已经得到了解决"
        },
        {
            "prefix": "",
            "pinyin": "xueshengmendouzairenzhengxuexi",
            "description": "Long multi-step: 学生们 → 都在 → 认真学习",
            "selections": [
                {"index": 0, "expected_contains": "学生"},
                {"index": 0, "expected_contains": "都"},
                {"index": 0, "expected_contains": "认真"}
            ],
            "final_sentence": "学生们都在认真学习"
        },
    ]
    
    # Category 5: Incremental building (very realistic)
    incremental_tests = [
        {
            "prefix": "",
            "pinyin": "zhongguoshidaguo",
            "description": "Incremental: 中国 → 是 → 大国",
            "selections": [
                {"index": 0, "expected_contains": "中国"},
                {"index": 0, "expected_contains": "是"},
                {"index": 0, "expected_contains": "大"}
            ],
            "final_sentence": "中国是大国"
        },
        {
            "prefix": "",
            "pinyin": "womendouaizuguo",
            "description": "Incremental: 我们 → 都 → 爱祖国",
            "selections": [
                {"index": 0, "expected_contains": "我们"},
                {"index": 0, "expected_contains": "都"},
                {"index": 0, "expected_contains": "爱"}
            ],
            "final_sentence": "我们都爱祖国"
        },
        {
            "prefix": "他说",
            "pinyin": "mingtianhuixialai",
            "description": "Incremental with prefix: 明天 → 会 → 下雨",
            "selections": [
                {"index": 0, "expected_contains": "明天"},
                {"index": 0, "expected_contains": "会"},
                {"index": 0, "expected_contains": "下"}
            ],
            "final_sentence": "明天会下雨"
        },
    ]
    
    # Combine all tests
    all_tests = (
        two_step_tests + 
        three_step_tests + 
        correction_tests + 
        long_multi_tests + 
        incremental_tests
    )
    
    # Add IDs
    for test in all_tests:
        test["id"] = test_id
        test_id += 1
    
    return all_tests

def save_test_cases(test_cases, filename="multi_selection_tests.json"):
    """Save test cases to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(test_cases)} multi-selection test cases")
    print(f"Saved to {filename}")
    
    # Print statistics
    two_step = len([t for t in test_cases if len(t['selections']) == 2])
    three_step = len([t for t in test_cases if len(t['selections']) == 3])
    with_prefix = len([t for t in test_cases if t['prefix']])
    
    print(f"\nBreakdown:")
    print(f"  Two-step selections: {two_step}")
    print(f"  Three-step selections: {three_step}")
    print(f"  With prefix: {with_prefix}")
    print(f"  Total: {len(test_cases)}")

if __name__ == "__main__":
    test_cases = generate_multi_selection_tests()
    save_test_cases(test_cases)
    
    # Show sample test
    print("\nSample test case:")
    sample = test_cases[1]
    print(f"  ID: {sample['id']}")
    print(f"  Description: {sample['description']}")
    print(f"  Prefix: '{sample['prefix']}'")
    print(f"  Pinyin: {sample['pinyin']}")
    print(f"  Selections: {len(sample['selections'])} steps")
    for i, sel in enumerate(sample['selections'], 1):
        print(f"    Step {i}: Select index {sel['index']}, expect '{sel['expected_contains']}'")
    print(f"  Final: {sample['final_sentence']}")
