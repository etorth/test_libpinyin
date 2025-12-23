#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate long sentence test cases for libpinyin
These test whole-sentence input capability
"""

import json

# Long sentences (real-world examples)
long_sentences = [
    {
        "sentence": "我看这个重大的政治问题已经得到了圆满的解决",
        "pinyin": "wokanzhegezhongdadezhengzhiwentiyijingdedaoleyuanmandejiejue",
        "description": "Political statement (21 chars)"
    },
    {
        "sentence": "今天天气非常好我们一起去公园玩吧",
        "pinyin": "jintiantianqifeichanghaowomenyiqiqugongyuanwanba",
        "description": "Weather and invitation (17 chars)"
    },
    {
        "sentence": "他昨天买了很多好吃的东西给大家",
        "pinyin": "tazuotianmailehenduohaochidedongxigeidajia",
        "description": "Shopping story (16 chars)"
    },
    {
        "sentence": "这是一个非常重要的历史时刻",
        "pinyin": "zheshiyigefeichangzhongyaodelishishike",
        "description": "Historical moment (14 chars)"
    },
    {
        "sentence": "我们应该认真学习科学技术知识",
        "pinyin": "womenyinggairenzhengxuexikexuejishuzhishi",
        "description": "Study encouragement (15 chars)"
    },
    {
        "sentence": "中国人民解放军是保卫祖国的钢铁长城",
        "pinyin": "zhongguorenminjiefangjunshibaoweizuguodegangtichangcheng",
        "description": "Military praise (18 chars - too long)"
    },
    {
        "sentence": "明天早上八点我要去机场接我的朋友",
        "pinyin": "mingtianzaoshangbadianyaoqujichagjiemewopengyou",
        "description": "Airport pickup (17 chars)"
    },
    {
        "sentence": "学生们都在教室里认真听老师讲课",
        "pinyin": "xueshengmendouzaijiaoshilirenzhentinglaoshijiangke",
        "description": "Classroom scene (16 chars)"
    },
    {
        "sentence": "春天来了公园里的花都开了",
        "pinyin": "chuntianlaile gongyuanlideuadoukaile",
        "description": "Spring scenery (13 chars)"
    },
    {
        "sentence": "我希望将来能够成为一名优秀的医生",
        "pinyin": "woxiwangjianglainenggouchengweiyimingyouxiudeyisheng",
        "description": "Career aspiration (17 chars)"
    },
    {
        "sentence": "这本书的内容非常丰富很值得阅读",
        "pinyin": "zhebenshudenerongfeichangfengfuhenhenszhideyuedu",
        "description": "Book review (16 chars)"
    },
    {
        "sentence": "请大家注意安全遵守交通规则",
        "pinyin": "qingdajiazuhuyianquanzunshoujiaotongguize",
        "description": "Safety reminder (14 chars)"
    },
    {
        "sentence": "今年的春节我要回家和家人团聚",
        "pinyin": "jinniandechunjieywaohuijiahejiaretunju",
        "description": "Spring Festival plan (15 chars)"
    },
    {
        "sentence": "互联网技术改变了我们的生活方式",
        "pinyin": "hulianwangjishuaibianlwomendeshenghuofangshi",
        "description": "Internet impact (16 chars)"
    },
    {
        "sentence": "保护环境是每个公民的责任和义务",
        "pinyin": "baohuhuanjingshimeigeongmindzerenheuwu",
        "description": "Environmental protection (16 chars)"
    },
]

# Add some incrementally longer sentences
incremental_sentences = [
    ("你好", "nihao", "2 chars"),
    ("你好吗", "nihaoma", "3 chars"),
    ("你好吗今天", "nihaomajintian", "5 chars"),
    ("你好吗今天天气", "nihaomajintiantianqi", "7 chars"),
    ("你好吗今天天气很好", "nihaomajintiantianqihenhao", "9 chars"),
    ("你好吗今天天气很好我们", "nihaomajintiantianqihenhaowomen", "11 chars"),
    ("你好吗今天天气很好我们一起", "nihaomajintiantianqihenhaowomenyiqi", "13 chars"),
    ("你好吗今天天气很好我们一起去玩", "nihaomajintiantianqihenhaowomenyiqiquwanr", "15 chars"),
    ("你好吗今天天气很好我们一起去玩儿吧", "nihaomajintiantianqihenhaowomenyiqiquwanrba", "17 chars - too long"),
]

def generate_long_test_cases():
    """Generate test cases for long sentences"""
    test_cases = []
    test_id = 1
    
    # Add long sentence tests
    for item in long_sentences:
        test_cases.append({
            "id": test_id,
            "prefix": "",
            "pinyin": item["pinyin"],
            "expected_contains": item["sentence"][:10],  # Check first 10 chars
            "full_sentence": item["sentence"],
            "description": f"Long: {item['description']}"
        })
        test_id += 1
    
    # Add incremental length tests
    for sentence, pinyin, desc in incremental_sentences:
        test_cases.append({
            "id": test_id,
            "prefix": "",
            "pinyin": pinyin,
            "expected_contains": sentence[:5] if len(sentence) > 5 else sentence,
            "full_sentence": sentence,
            "description": f"Length test: {desc}"
        })
        test_id += 1
    
    # Add tests with prefixes for long sentences
    prefixes = ["我觉得", "大家都说", "据说", "事实上"]
    for i, item in enumerate(long_sentences[:5]):  # First 5 with prefixes
        for prefix in prefixes[:2]:  # First 2 prefixes
            test_cases.append({
                "id": test_id,
                "prefix": prefix,
                "pinyin": item["pinyin"],
                "expected_contains": item["sentence"][:8],
                "full_sentence": item["sentence"],
                "description": f"Long with prefix '{prefix}': {item['sentence'][:10]}..."
            })
            test_id += 1
    
    return test_cases

def save_test_cases(test_cases, filename="long_sentence_tests.json"):
    """Save test cases to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(test_cases)} long sentence test cases")
    print(f"Saved to {filename}")

if __name__ == "__main__":
    test_cases = generate_long_test_cases()
    save_test_cases(test_cases)
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Long sentences: {len(long_sentences)}")
    print(f"  Incremental tests: {len(incremental_sentences)}")
    print(f"  With prefix tests: {len(test_cases) - len(long_sentences) - len(incremental_sentences)}")
    print(f"  Total: {len(test_cases)}")
    
    # Show length distribution
    print("\nLength distribution:")
    for item in long_sentences:
        length = len(item['sentence'])
        status = "✓" if length < 16 else "✗ (too long)"
        print(f"  {length:2d} chars {status}: {item['sentence'][:30]}...")
