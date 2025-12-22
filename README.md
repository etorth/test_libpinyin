# test_libpinyin

A Chinese pinyin input method test program using libpinyin.

## Features

- **User preference learning**: Remembers your phrase selections and offers them as candidates in future inputs
- **Context-aware suggestions**: Learns bigram relationships between phrases over time
- **Persistent storage**: All learned preferences are saved and available after program restart
- **Incomplete pinyin handling**: Only saves complete pinyin phrases to dictionary

## Usage

```bash
make
./a.out
```

### Input Flow

1. **Prefix**: Enter previous context (Chinese characters) or press Enter to skip
2. **Pinyin**: Enter pinyin for the phrase you want to type
3. **Choose**: Select candidates by number until the sentence is complete
4. Type `quit` to exit

### Example

```
prefix (Chinese chars): 我是
pinyin: niba
0:泥巴(2)  1:你爸(2)  ...
choose: 1
sentence: 你爸
```

## How Prefix/Context Learning Works

The prefix feature uses **statistical bigram learning** implemented in libpinyin:

### Training Process:
1. When you enter prefix "我吃" and select "泥巴" for "niba", the system records this transition
2. `pinyin_train()` updates the bigram probability model  
3. `pinyin_remember_user_input()` saves the phrase-pinyin association
4. Data is saved to `data/user_bigram.db`

### How It Affects Ranking:
- libpinyin automatically consults the bigram model during `pinyin_guess_candidates()`
- After the SAME prefix→phrase pattern is selected **10-20 times**, the ranking will noticeably improve
- Different prefixes build independent statistics: "我吃"→"泥巴" vs "我是"→"你爸"

### Example:
```bash
# First 10-15 times with prefix "我吃" + "niba" → select "泥巴"
# Learning: '我吃' → '泥巴'

# Then try prefix "我是" + "niba" → select "你爸" 10-15 times  
# Learning: '我是' → '你爸'

# After sufficient training:
# With prefix "我吃": "泥巴" ranks higher
# With prefix "我是": "你爸" ranks higher
```

**Note**: This is how all modern IMEs work (including ibus-libpinyin). The system learns from your usage patterns over time rather than providing immediate changes.

## Files

- `main.cpp`: Main program source
- `data/`: libpinyin data files (system and user dictionaries)
- `data/user.bin`, `data/user_bigram.db`: User-learned phrases and bigrams