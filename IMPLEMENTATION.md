# Implementation Details

## Overview
This is a command-line pinyin input method based on libpinyin, following the architectural patterns of ibus-libpinyin.

## Key Learnings from ibus-libpinyin

### 1. Candidate Selection Architecture
From studying `PYPLibPinyinCandidates.cc`:

```cpp
// Different candidate types require different handling:
- NBEST_MATCH: Full sentence, start from position 0
- LONGER/LONGER_USER: Longer phrases, start from position 0  
- NORMAL/USER: Regular incremental selection
```

### 2. Training Strategy
From `PYPLibPinyinCandidates::selectCandidate()`:

```cpp
// For NBEST candidates:
pinyin_choose_candidate(instance, 0, candidate);
if (index != 0)
    pinyin_train(instance, index);  // Train with nbest index
pinyin_get_sentence(instance, index, &str);
if (rememberEveryInput)
    pinyin_remember_user_input(instance, str, -1);
```

```cpp
// For normal candidates after full input:
pinyin_choose_candidate(instance, lookup_cursor, candidate);
pinyin_guess_sentence(instance);  // Predict remaining
if (lookup_cursor == text.length()) {
    pinyin_train(instance, 0);
    pinyin_remember_user_input(instance, str, -1);
}
```

### 3. Learning Mechanisms

#### A. pinyin_train()
- Updates bigram probability model
- Learns phrase transitions: P(phrase_B | phrase_A)
- Stored in `data/user_bigram.db`
- Consulted automatically during `pinyin_guess_candidates()`

#### B. pinyin_remember_user_input()
- Records phrase-pinyin association
- Stores in user phrase/pinyin index files
- Makes phrases available as candidates
- Called AFTER training

#### C. User Dictionary Import
- For complete pinyin only
- Direct phrase lookup
- Higher frequency for user phrases

## Implementation Features

### Complete Feature List
✅ **Incremental Selection**: Character-by-character or full sentence
✅ **NBEST Handling**: Full sentence predictions
✅ **Bigram Training**: Context-aware suggestions via `pinyin_train()`
✅ **User Input Memory**: `pinyin_remember_user_input()` integration
✅ **Sentence Guessing**: `pinyin_guess_sentence()` for predictions
✅ **Complete/Incomplete Validation**: Only save valid pinyin
✅ **Persistent Storage**: Auto-save with `pinyin_save()`
✅ **User Dictionary**: Direct phrase-pinyin import
✅ **Config Options**: REMEMBER_EVERY_INPUT flag

### Flow Diagram

```
User Input "nihao"
    ↓
pinyin_parse_more_full_pinyins()
    ↓
Check pinyin completeness
    ↓
┌─────────────────────────────┐
│  Selection Loop             │
│  ↓                          │
│  pinyin_guess_candidates()  │
│  ↓                          │
│  Display & Select           │
│  ↓                          │
│  pinyin_choose_candidate()  │
│  ↓                          │
│  pinyin_guess_sentence()    │ ← Predict rest
│  ↓                          │
│  Continue if not finished   │
└─────────────────────────────┘
    ↓
pinyin_train(instance, 0)      ← Train bigram
    ↓
pinyin_remember_user_input()   ← Remember phrase
    ↓
add_to_user_dictionary()       ← If complete
    ↓
pinyin_save()                  ← Persist
```

## Prefix/Context Learning

### How It Works
The "prefix" feature uses bigram learning:

1. **Record Transition**: When selecting phrase B after phrase A
2. **Update Model**: `pinyin_train()` increases P(B|A)
3. **Automatic Consultation**: `pinyin_guess_candidates()` uses bigram model
4. **Gradual Improvement**: After 10-20 repetitions, ranking improves

### Example Training Cycle
```
Input Sequence:
1. prefix="我吃", input="niba", select="泥巴"  → Learn: P(泥巴|我吃)++
2. prefix="我吃", input="niba", select="泥巴"  → Learn: P(泥巴|我吃)++
...
10. prefix="我吃", input="niba"
    → "泥巴" now ranks higher due to stronger P(泥巴|我吃)

Separately:
1. prefix="我是", input="niba", select="你爸"  → Learn: P(你爸|我是)++
...
```

### Why It Takes Time
- Statistical model needs sufficient data
- Competing probabilities from system dictionary
- User patterns override system defaults gradually
- This is standard behavior in all IMEs (Google Pinyin, Sogou, etc.)

## File Structure

### Data Files
- `data/user.bin` - User dictionary metadata
- `data/user_bigram.db` - Bigram statistics (SQLite)
- `data/user_phrase_index.bin` - User phrase storage
- `data/user_pinyin_index.bin` - Pinyin key index
- `data/user.conf` - User configuration

### Code Structure
```
main.cpp:
├── read_line()                    # Input handling
├── display_candidates()           # Show options
├── select_candidate()             # Handle selection (NBEST aware)
├── process_pinyin_input()         # Main selection loop
├── add_to_user_dictionary()       # Direct phrase import
├── learn_and_save()               # Training & persistence
└── main()                         # Program flow
```

## Comparison with ibus-libpinyin

### What We Implemented
✅ Core selection logic
✅ NBEST candidate handling
✅ Training strategy
✅ Remember user input
✅ Sentence guessing
✅ Persistent storage

### What We Simplified
- No GUI/IBus integration
- No English/Emoji/Lua extensions
- No cloud input
- No traditional Chinese conversion
- Single configuration (REMEMBER_EVERY_INPUT=true)
- Command-line only

### What's the Same
- libpinyin API usage patterns
- Training/learning strategy
- Bigram model integration
- Persistence mechanism

## Testing

### Basic Usage
```bash
./a.out
prefix (Chinese chars): 
pinyin: nihao
choose: 0
sentence: 你好
```

### Testing Bigram Learning
```bash
# Train pattern: "我吃" → "泥巴"
for i in {1..15}; do
    echo -e "\n\n我吃\nniba\n0\n"
done | ./a.out

# Test: Should eventually prefer "泥巴" after "我吃"
```

## References
- libpinyin API: `/usr/include/libpinyin-2.8.1/pinyin.h`
- ibus-libpinyin source: `/home/anhong/ibus-libpinyin/src/`
- Key files studied:
  - `PYPLibPinyinCandidates.cc` - Candidate selection logic
  - `PYPPhoneticEditor.cc` - Editor behavior
  - `PYLibPinyin.cc` - Backend interface
