#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate test cases for libpinyin test_pinyin program
"""

import random
import json

# Common Chinese phrases with their pinyin
test_data = [
    # Basic greetings
    ("你好", "nihao"),
    ("早上好", "zaoshanghao"),
    ("晚上好", "wanshanghao"),
    ("再见", "zaijian"),
    ("谢谢", "xiexie"),
    ("对不起", "duibuqi"),
    
    # Common phrases
    ("我爱你", "woaini"),
    ("我想你", "woxiangni"),
    ("没关系", "meiguanxi"),
    ("不客气", "bukeqi"),
    ("加油", "jiayou"),
    ("好的", "haode"),
    ("是的", "shide"),
    ("不是", "bushi"),
    
    # Food
    ("吃饭", "chifan"),
    ("喝水", "heshui"),
    ("苹果", "pingguo"),
    ("香蕉", "xiangjiao"),
    ("西瓜", "xigua"),
    ("米饭", "mifan"),
    ("面条", "miantiao"),
    ("饺子", "jiaozi"),
    
    # Daily life
    ("上班", "shangban"),
    ("下班", "xiaban"),
    ("睡觉", "shuijiao"),
    ("起床", "qichuang"),
    ("洗澡", "xizao"),
    ("看书", "kanshu"),
    ("学习", "xuexi"),
    ("工作", "gongzuo"),
    
    # Places
    ("学校", "xuexiao"),
    ("公司", "gongsi"),
    ("医院", "yiyuan"),
    ("银行", "yinhang"),
    ("超市", "chaoshi"),
    ("饭店", "fandian"),
    ("机场", "jichang"),
    ("火车站", "huochezhan"),
    
    # Weather
    ("天气", "tianqi"),
    ("晴天", "qingtian"),
    ("下雨", "xiayu"),
    ("下雪", "xiaxue"),
    ("刮风", "guafeng"),
    ("很热", "henre"),
    ("很冷", "henleng"),
    
    # Numbers and time
    ("一", "yi"),
    ("二", "er"),
    ("三", "san"),
    ("十", "shi"),
    ("百", "bai"),
    ("千", "qian"),
    ("万", "wan"),
    ("今天", "jintian"),
    ("明天", "mingtian"),
    ("昨天", "zuotian"),
    
    # Longer phrases
    ("我是学生", "woshixuesheng"),
    ("你叫什么名字", "nijiaoshenmemingzi"),
    ("我很高兴", "wohengaoxing"),
    ("太好了", "taihaole"),
    ("非常感谢", "feichangganxie"),
    ("祝你好运", "zhunihaoyun"),
    ("一路平安", "yilupingan"),
    ("身体健康", "shentijiankang"),
    
    # Sentences
    ("我爱中国", "woaizhongguo"),
    ("今天天气很好", "jintiantianqihenhao"),
    ("我去上班", "woqushangban"),
    ("他是我朋友", "tashiwopengyou"),
    ("我们一起吃饭", "womenyiqichifan"),
    ("这个很好吃", "zhegehenhaochi"),
    ("那个不好看", "nagebuhaokan"),
    
    # Common expressions
    ("加油站", "jiayouzhan"),
    ("红绿灯", "honglvdeng"),
    ("出租车", "chuzuche"),
    ("公共汽车", "gonggongqiche"),
    ("地铁站", "ditiezhan"),
    ("电影院", "dianyingyuan"),
    ("图书馆", "tushuguan"),
    ("咖啡厅", "kafeiting"),
    
    # Family
    ("爸爸", "baba"),
    ("妈妈", "mama"),
    ("哥哥", "gege"),
    ("姐姐", "jiejie"),
    ("弟弟", "didi"),
    ("妹妹", "meimei"),
    ("爷爷", "yeye"),
    ("奶奶", "nainai"),
    
    # Actions
    ("走路", "zoulu"),
    ("跑步", "paobu"),
    ("游泳", "youyong"),
    ("打球", "daqiu"),
    ("唱歌", "changge"),
    ("跳舞", "tiaowu"),
    ("画画", "huahua"),
    ("写字", "xiezi"),
    
    # Colors
    ("红色", "hongse"),
    ("蓝色", "lanse"),
    ("绿色", "lvse"),
    ("黄色", "huangse"),
    ("黑色", "heise"),
    ("白色", "baise"),
    ("紫色", "zise"),
    ("粉色", "fense"),
]

# Prefixes for context testing
prefixes = [
    "",  # No prefix
    "我",
    "你",
    "他",
    "我们",
    "今天",
    "明天",
    "我想",
    "我要",
    "可以",
    "不要",
    "很好",
    "非常",
    "特别",
    "真的",
    "确实",
    "一定",
    "应该",
    "可能",
    "也许",
    "当然",
]

# Long sentence test cases (edge cases)
long_phrases = [
    ("我今天要去学校", "wojintianraoqvxuexiao"),  # Intentional typo to test
    ("你明天有时间吗", "nimingtianyoushijianjma"),  # ma typo
    ("我们一起吃晚饭", "womenyiqichiwaanfan"),  # waan typo
    ("这是我的好朋友", "zheshiwodehaopenngyou"),  # penn typo
    ("他很喜欢看电影", "tahenxihuankandianying"),
    ("我要买很多东西", "woyaomaihennduodongxi"),  # henn typo
    ("今天天气真不错", "jintiantianqizhenbuucuo"),  # buu typo
    ("我们明天见面吧", "womenmingtianjianmianba"),
]

def generate_test_cases(num_tests=200):
    """Generate test cases for libpinyin"""
    test_cases = []
    
    # Test 1-50: Basic phrases without prefix
    for i in range(50):
        phrase, pinyin = random.choice(test_data)
        test_cases.append({
            "id": i + 1,
            "prefix": "",
            "pinyin": pinyin,
            "expected_contains": phrase,
            "description": f"Basic: {phrase}"
        })
    
    # Test 51-100: Phrases with prefix context
    for i in range(50):
        prefix = random.choice(prefixes)
        phrase, pinyin = random.choice(test_data)
        test_cases.append({
            "id": i + 51,
            "prefix": prefix,
            "pinyin": pinyin,
            "expected_contains": phrase,
            "description": f"With prefix '{prefix}': {phrase}"
        })
    
    # Test 101-120: Long phrases
    for i in range(20):
        prefix = random.choice(["", "我觉得", "我认为", "我看到"])
        phrase, pinyin = random.choice(test_data)
        # Create longer sentences
        phrase2, pinyin2 = random.choice(test_data)
        combined = phrase + phrase2
        combined_pinyin = pinyin + pinyin2
        if len(combined) <= 15:  # Respect MAX_PHRASE_LENGTH
            test_cases.append({
                "id": i + 101,
                "prefix": prefix,
                "pinyin": combined_pinyin,
                "expected_contains": combined[:len(phrase)],  # Just check first part
                "description": f"Long: {combined}"
            })
    
    # Test 121-150: Repeated inputs (test memory)
    repeated_phrases = [
        ("你好", "nihao"),
        ("谢谢", "xiexie"),
        ("我爱你", "woaini"),
        ("吃饭", "chifan"),
        ("再见", "zaijian"),
    ]
    for i in range(30):
        phrase, pinyin = repeated_phrases[i % len(repeated_phrases)]
        prefix = random.choice(["", "我想说", "你知道"])
        test_cases.append({
            "id": i + 121,
            "prefix": prefix,
            "pinyin": pinyin,
            "expected_contains": phrase,
            "description": f"Repeat test: {phrase}"
        })
    
    # Test 151-170: Edge cases with typos
    for i in range(20):
        if i < len(long_phrases):
            phrase, pinyin = long_phrases[i]
        else:
            phrase, pinyin = random.choice(test_data)
        test_cases.append({
            "id": i + 151,
            "prefix": "",
            "pinyin": pinyin,
            "expected_contains": None,  # May fail, that's ok
            "description": f"Edge case: {pinyin}"
        })
    
    # Test 171-200: Mixed complexity
    for i in range(30):
        prefix = random.choice(prefixes + ["今天我", "我们的", "这个是", "那个是"])
        phrase, pinyin = random.choice(test_data)
        test_cases.append({
            "id": i + 171,
            "prefix": prefix,
            "pinyin": pinyin,
            "expected_contains": phrase,
            "description": f"Mixed: prefix='{prefix}', phrase={phrase}"
        })
    
    return test_cases

def save_test_cases(test_cases, filename="test_cases.json"):
    """Save test cases to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(test_cases)} test cases and saved to {filename}")

if __name__ == "__main__":
    test_cases = generate_test_cases(200)
    save_test_cases(test_cases)
    
    # Print summary
    print("\nTest Case Summary:")
    print(f"  1-50:   Basic phrases without prefix")
    print(f"  51-100: Phrases with prefix context")
    print(f"  101-120: Long combined phrases")
    print(f"  121-150: Repeated inputs (memory test)")
    print(f"  151-170: Edge cases with potential typos")
    print(f"  171-200: Mixed complexity tests")
