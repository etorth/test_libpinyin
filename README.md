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

The prefix feature uses **bigram learning** which builds up over time:

1. When you enter prefix "我是" and then select "你爸" for "niba", the system learns this transition
2. The more you make this selection, the stronger the association becomes
3. After several training iterations, "你爸" will be ranked higher when the prefix is "我是"

**Note**: Context-aware ranking requires training data. The first few times you'll need to manually select the correct candidate. After repeated use, the system learns your patterns and offers better suggestions.

## Files

- `main.cpp`: Main program source
- `data/`: libpinyin data files (system and user dictionaries)
- `data/user.bin`, `data/user_bigram.db`: User-learned phrases and bigrams