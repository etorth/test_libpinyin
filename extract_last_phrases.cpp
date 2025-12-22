/*
 * Example: Extract last 1-2 phrases from Chinese text using libpinyin
 * 
 * Compile: g++ extract_last_phrases.cpp `pkg-config libpinyin --libs --cflags` -o extract_phrases
 * Usage: ./extract_phrases "不管其他啥事，如果只讨论今晚吃啥，我吃"
 */

#include "pinyin.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <vector>

// Extract last N phrases from text using libpinyin's phrase segmentation
std::string get_last_phrases(pinyin_context_t* context, pinyin_instance_t* instance,
                             const char* text, int num_phrases = 2) {
    if (!text || strlen(text) == 0) {
        return "";
    }
    
    // Use libpinyin to segment the text into phrases
    if (!pinyin_phrase_segment(instance, text)) {
        fprintf(stderr, "Failed to segment phrase\n");
        return "";
    }
    
    // Get number of phrases
    guint num = 0;
    pinyin_get_n_phrase(instance, &num);
    
    if (num == 0) {
        return "";
    }
    
    printf("Total phrases found: %u\n", num);
    
    // Calculate starting index for last N phrases
    guint start_idx = (num > (guint)num_phrases) ? (num - num_phrases) : 0;
    
    // Extract last N phrase tokens
    std::vector<phrase_token_t> tokens;
    for (guint i = start_idx; i < num; i++) {
        phrase_token_t token;
        if (pinyin_get_phrase_token(instance, i, &token)) {
            tokens.push_back(token);
        }
    }
    
    // Convert tokens back to text
    std::string result;
    for (size_t i = 0; i < tokens.size(); i++) {
        guint len = 0;
        gchar* phrase_str = NULL;
        
        if (pinyin_token_get_phrase(instance, tokens[i], &len, &phrase_str)) {
            if (phrase_str) {
                printf("Phrase %zu: %s (length: %u)\n", i, phrase_str, len);
                result += phrase_str;
                g_free(phrase_str);
            }
        }
    }
    
    return result;
}

// Alternative: Extract text after last punctuation
std::string get_after_last_punctuation(const char* text) {
    if (!text || strlen(text) == 0) {
        return "";
    }
    
    const char* punctuation[] = {"。", "！", "？", "；", "，", nullptr};
    size_t last_pos = 0;
    
    for (int i = 0; punctuation[i]; i++) {
        const char* pos = strrchr(text, punctuation[i][0]);
        if (pos && (size_t)(pos - text) > last_pos) {
            last_pos = pos - text;
        }
    }
    
    if (last_pos > 0) {
        // Skip the punctuation mark (3 bytes for UTF-8 Chinese punctuation)
        const char* after = text + last_pos;
        // Find next character after punctuation
        while (*after && (*after & 0xC0) == 0x80) after++; // Skip UTF-8 continuation bytes
        if (*after) after += 1; // Skip first byte of next char
        while (*after && (*after & 0xC0) == 0x80) after++; // Skip its continuation bytes
        
        return std::string(after);
    }
    
    return std::string(text);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s \"Chinese text\"\n", argv[0]);
        fprintf(stderr, "Example: %s \"不管其他啥事，如果只讨论今晚吃啥，我吃\"\n", argv[0]);
        return 1;
    }
    
    const char* text = argv[1];
    
    printf("Input text: %s\n", text);
    printf("=================================\n\n");
    
    // Method 1: Using libpinyin phrase segmentation
    printf("Method 1: libpinyin phrase segmentation\n");
    printf("-----------------------------------------\n");
    
    pinyin_context_t* context = pinyin_init("/usr/lib/x86_64-linux-gnu/libpinyin/data", NULL);
    if (!context) {
        fprintf(stderr, "Failed to initialize pinyin context\n");
        return 1;
    }
    
    pinyin_instance_t* instance = pinyin_alloc_instance(context);
    if (!instance) {
        fprintf(stderr, "Failed to allocate instance\n");
        pinyin_fini(context);
        return 1;
    }
    
    std::string last_1_phrase = get_last_phrases(context, instance, text, 1);
    printf("Last 1 phrase: %s\n\n", last_1_phrase.c_str());
    
    pinyin_reset(instance);
    
    std::string last_2_phrases = get_last_phrases(context, instance, text, 2);
    printf("Last 2 phrases: %s\n\n", last_2_phrases.c_str());
    
    // Method 2: Simple punctuation-based extraction
    printf("\nMethod 2: After last punctuation\n");
    printf("-----------------------------------------\n");
    std::string after_punct = get_after_last_punctuation(text);
    printf("After punctuation: %s\n\n", after_punct.c_str());
    
    // Cleanup
    pinyin_free_instance(instance);
    pinyin_fini(context);
    
    printf("\n=================================\n");
    printf("Recommendation for bigram context:\n");
    printf("  Use last 1-2 phrases: %s\n", last_2_phrases.c_str());
    
    return 0;
}
