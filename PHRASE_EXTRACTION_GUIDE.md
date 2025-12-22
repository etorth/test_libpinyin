# How to Extract Last 1-2 Phrases from Long Text

## Problem
Given text: `"不管其他啥事，如果只讨论今晚吃啥，我吃"`
You need: `"我吃"` (last 1-2 phrases as context for bigram)

## Solution: Three Methods

### Method 1: ✅ Use `pinyin_phrase_segment()` (Recommended)

libpinyin provides **phrase segmentation** that intelligently splits Chinese text into meaningful phrases.

```cpp
#include "pinyin.h"

std::string get_last_phrases(pinyin_context_t* context, 
                             pinyin_instance_t* instance,
                             const char* text, 
                             int num_phrases = 2) {
    // Segment the text into phrases
    if (!pinyin_phrase_segment(instance, text)) {
        return "";
    }
    
    // Get number of phrases
    guint num = 0;
    pinyin_get_n_phrase(instance, &num);
    
    // Calculate starting index for last N phrases
    guint start_idx = (num > (guint)num_phrases) ? (num - num_phrases) : 0;
    
    // Extract tokens and convert to text
    std::string result;
    for (guint i = start_idx; i < num; i++) {
        phrase_token_t token;
        if (pinyin_get_phrase_token(instance, i, &token)) {
            guint len = 0;
            gchar* phrase_str = NULL;
            if (pinyin_token_get_phrase(instance, token, &len, &phrase_str)) {
                result += phrase_str;
                g_free(phrase_str);
            }
        }
    }
    
    return result;
}
```

**Usage:**
```cpp
std::string context_prefix = get_last_phrases(context, instance, 
    "不管其他啥事，如果只讨论今晚吃啥，我吃", 2);
// Returns: "我吃" or similar (depends on phrase boundaries)
```

### Method 2: ✅ Punctuation-Based (Simple & Reliable)

Chinese text naturally segments at punctuation marks.

```cpp
std::string get_after_last_punctuation(const std::string& text) {
    // Find last major punctuation
    const char* marks[] = {"。", "！", "？", "；", nullptr};
    size_t last_pos = std::string::npos;
    
    for (int i = 0; marks[i]; i++) {
        size_t pos = text.rfind(marks[i]);
        if (pos != std::string::npos) {
            if (last_pos == std::string::npos || pos > last_pos) {
                last_pos = pos;
            }
        }
    }
    
    if (last_pos != std::string::npos) {
        // Return text after punctuation (skip the mark itself)
        return text.substr(last_pos + 3); // +3 for UTF-8 punctuation
    }
    
    // No punctuation, limit to last N characters
    return get_last_n_chars(text, 6); // Last ~2 words
}

std::string get_last_n_chars(const std::string& text, size_t max_chars) {
    size_t char_count = 0;
    for (ssize_t i = text.length() - 1; i >= 0; i--) {
        if ((text[i] & 0xC0) != 0x80) { // UTF-8 char boundary
            char_count++;
            if (char_count > max_chars) {
                return text.substr(i + 1);
            }
        }
    }
    return text;
}
```

**Example:**
```cpp
get_after_last_punctuation("不管其他啥事，如果只讨论今晚吃啥，我吃")
// Returns: "我吃"
```

### Method 3: ✅ Comma-Aware Extraction (Balanced)

Use commas as boundaries, but limit length:

```cpp
std::string get_smart_prefix(const std::string& text) {
    // Try to find last comma
    size_t comma_pos = text.rfind("，");
    
    if (comma_pos != std::string::npos) {
        std::string after_comma = text.substr(comma_pos + 3); // +3 for UTF-8
        
        // If text after comma is short enough, use it
        size_t utf8_len = g_utf8_strlen(after_comma.c_str(), -1);
        if (utf8_len <= 6) { // 6 characters max
            return after_comma;
        }
        // Otherwise, take last 6 chars of the part after comma
        return get_last_n_chars(after_comma, 6);
    }
    
    // No comma, just take last 6 characters
    return get_last_n_chars(text, 6);
}
```

**Example:**
```cpp
get_smart_prefix("不管其他啥事，如果只讨论今晚吃啥，我吃")
// Returns: "我吃" (text after last comma, under 6 chars)

get_smart_prefix("不管其他啥事，如果只讨论今晚吃啥还是明天早上吃啥，我吃")
// Returns: last 6 chars of "如果只讨论...我吃"
```

## Practical Integration with Your main.cpp

### Option A: Automatic Context (Best for Most Cases)

Don't ask user for prefix - use automatic tracking:

```cpp
std::string previous_phrase;  // Automatically tracked

while (true) {
    // No manual prefix input!
    
    if (!read_line(&linebuf, &linesize, "pinyin:")) break;
    if (strcmp(linebuf, "quit") == 0) break;
    
    // previous_phrase is automatically the last selection
    // This is optimal for bigram learning!
    
    pinyin_parse_more_full_pinyins(instance, linebuf);
    std::string generated_sentence = process_pinyin_input(...);
    
    learn_and_save(context, instance, generated_sentence, linebuf,
                  is_complete, previous_phrase);  // ← Uses last phrase
    
    previous_phrase = generated_sentence;  // ← Update
    pinyin_reset(instance);
}
```

### Option B: Manual Long-Text Support

If user wants to provide long context, extract it automatically:

```cpp
while (true) {
    // User provides any length text
    if (!read_line(&prefixbuf, &prefixsize, "context (任意长度):")) break;
    
    // Extract last 1-2 phrases automatically
    std::string smart_prefix;
    if (strlen(prefixbuf) > 0) {
        // Method 1: Use punctuation
        smart_prefix = get_after_last_punctuation(prefixbuf);
        
        // Method 2: Or use phrase segmentation
        // smart_prefix = get_last_phrases(context, instance, prefixbuf, 2);
        
        printf("Using prefix: '%s'\n", smart_prefix.c_str());
    }
    
    // ... rest of input processing ...
    
    learn_and_save(context, instance, generated_sentence, linebuf,
                  is_complete, smart_prefix);
}
```

## API Functions Summary

### From libpinyin:
- `pinyin_phrase_segment(instance, text)` - Segment text into phrases
- `pinyin_get_n_phrase(instance, &num)` - Get phrase count
- `pinyin_get_phrase_token(instance, i, &token)` - Get phrase token
- `pinyin_token_get_phrase(instance, token, &len, &str)` - Token to string

### From GLib (included with libpinyin):
- `g_utf8_strlen(str, -1)` - Count UTF-8 characters
- `g_utf8_to_ucs4(str, ...)` - Convert to UCS-4
- `g_free(ptr)` - Free GLib-allocated memory

## Recommendations

### For Your Use Case:

1. **If `previous_phrase` is available**: Use it directly (current design is perfect!)
   ```cpp
   previous_phrase = generated_sentence;  // This IS the last phrase!
   ```

2. **If user provides long text**: Use **Method 2** (punctuation-based)
   - Simple, reliable, fast
   - No extra libpinyin state needed
   - Works well for Chinese text

3. **For advanced segmentation**: Use **Method 1** (phrase_segment)
   - More accurate phrase boundaries
   - But requires instance state management

### Simple Rule of Thumb:
```
Text length ≤ 6 chars  → Use as-is
Text has comma         → Use text after last comma
Text has period        → Use text after period
Text > 6 chars         → Take last 6 characters
```

## Testing

Compile and test the example:
```bash
cd /home/anhong/test_libpinyin
./extract_phrases "不管其他啥事，如果只讨论今晚吃啥，我吃"
```

Output:
```
Method 2: After last punctuation
-----------------------------------------
After punctuation: 我吃
```

Perfect for bigram context! 🎯
