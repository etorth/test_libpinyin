// Helper function to add to main.cpp
// Extracts smart context from potentially long text

#include <string>
#include <cstring>

// Extract last N Chinese characters from UTF-8 string
std::string get_last_n_chars(const std::string& text, size_t max_chars) {
    if (text.empty()) return "";
    
    // Count backwards from the end
    size_t char_count = 0;
    ssize_t byte_pos = text.length();
    
    while (byte_pos > 0 && char_count < max_chars) {
        byte_pos--;
        // If this byte is NOT a UTF-8 continuation byte (10xxxxxx)
        if ((text[byte_pos] & 0xC0) != 0x80) {
            char_count++;
        }
    }
    
    // If we haven't reached max_chars, return entire string
    if (char_count < max_chars) {
        return text;
    }
    
    // Move forward to the next character boundary if we're in the middle
    while (byte_pos < (ssize_t)text.length() && (text[byte_pos] & 0xC0) == 0x80) {
        byte_pos++;
    }
    
    return text.substr(byte_pos);
}

// Smart prefix extraction - handles long text automatically
std::string extract_smart_prefix(const std::string& text, size_t max_chars = 4) {
    if (text.empty()) return "";
    
    // Strategy 1: Look for last major punctuation
    const char* major_punct[] = {"。", "！", "？", "；", nullptr};
    size_t last_major = std::string::npos;
    
    for (int i = 0; major_punct[i]; i++) {
        size_t pos = text.rfind(major_punct[i]);
        if (pos != std::string::npos && 
            (last_major == std::string::npos || pos > last_major)) {
            last_major = pos;
        }
    }
    
    if (last_major != std::string::npos) {
        // Found major punctuation - use text after it
        std::string after = text.substr(last_major + 3); // +3 for UTF-8
        return get_last_n_chars(after, max_chars);
    }
    
    // Strategy 2: Look for last comma
    size_t last_comma = text.rfind("，");
    if (last_comma != std::string::npos) {
        std::string after = text.substr(last_comma + 3); // +3 for UTF-8
        return get_last_n_chars(after, max_chars);
    }
    
    // Strategy 3: No punctuation - just take last N chars
    return get_last_n_chars(text, max_chars);
}

// Usage examples:
int main() {
    // Example 1: Long text with comma
    std::string long_text = "不管其他啥事，如果只讨论今晚吃啥，我吃";
    std::string prefix = extract_smart_prefix(long_text);
    printf("From: %s\n", long_text.c_str());
    printf("Prefix: %s\n\n", prefix.c_str());
    // Output: "我吃"
    
    // Example 2: Short text - use as-is
    std::string short_text = "我吃";
    prefix = extract_smart_prefix(short_text);
    printf("From: %s\n", short_text.c_str());
    printf("Prefix: %s\n\n", prefix.c_str());
    // Output: "我吃"
    
    // Example 3: No punctuation - take last 4 chars
    std::string no_punct = "今天天气很好我很开心";
    prefix = extract_smart_prefix(no_punct);
    printf("From: %s\n", no_punct.c_str());
    printf("Prefix: %s\n\n", prefix.c_str());
    // Output: "我很开心"
    
    return 0;
}

/* 
   To integrate into your main.cpp:
   
   1. Add these functions before main()
   2. In main loop, replace:
   
      previous_phrase = prefixbuf;
      
      with:
      
      previous_phrase = extract_smart_prefix(prefixbuf, 4);
      printf("Using context: '%s'\n", previous_phrase.c_str());
*/
