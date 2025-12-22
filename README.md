# test_libpinyin

A Chinese pinyin input method test program using libpinyin, following ibus-libpinyin's design patterns.

## Features

### Core Functionality
- **Incremental candidate selection**: Select phrases character by character or as complete sentences
- **NBEST match handling**: Full sentence predictions when available (candidate type 2)
- **User preference learning**: Remembers your phrase selections via `pinyin_remember_user_input()`
- **Bigram training**: Learns phrase transitions through `pinyin_train()` for context-aware suggestions
- **Persistent storage**: All learned preferences saved to `data/user_bigram.db` and user dictionaries
- **Complete/incomplete pinyin validation**: Only saves valid complete pinyin to user dictionary

### Learning Mechanisms
1. **Phrase-Pinyin Association**: Direct phrase to pinyin mapping in user dictionary
2. **Bigram Model**: Statistical model of phrase transitions (e.g., "我吃" → "泥巴")
3. **Sentence Guessing**: Uses `pinyin_guess_sentence()` after each selection for better predictions

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

## Implementation Details

### Based on ibus-libpinyin Architecture
This implementation follows the same patterns used in ibus-libpinyin:

1. **Candidate Selection Flow**:
   - `pinyin_parse_more_full_pinyins()` - Parse input
   - `pinyin_guess_candidates()` - Generate candidates for current position
   - `pinyin_choose_candidate()` - Select a candidate
   - `pinyin_guess_sentence()` - Predict rest of sentence
   - `pinyin_train()` - Train bigram model
   - `pinyin_remember_user_input()` - Remember phrase-pinyin association
   - `pinyin_save()` - Persist to disk

2. **Candidate Types**:
   - **NBEST_MATCH (2)**: Full sentence match covering entire input
   - **Normal (0)**: Regular phrase candidates
   - **User candidates**: Phrases from user dictionary

3. **Training Strategy**:
   - Train with nbest index if not top choice
   - Train at position 0 after all selections
   - Remember user input for phrase-pinyin learning
   - Save immediately for persistence

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