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

int main(int argc, char* argv[]) {

    if (argc < 2) {
        fprintf(stderr, "Usage: %s \"Chinese text\"\n", argv[0]);
        fprintf(stderr, "Example: %s \"不管其他啥事，如果只讨论今晚吃啥，我吃\"\n", argv[0]);
        return 1;
    }

    // Create user.conf if it doesn't exist to avoid warning message
    FILE* check_file = fopen("data/user.conf", "r");
    if (!check_file) {
        FILE* create_file = fopen("data/user.conf", "w");
        if (create_file) {
            fclose(create_file);
        }
    }
    else {
        fclose(check_file);
    }

    const char* text = argv[1];

    printf("Input text: %s\n", text);
    printf("=================================\n\n");

    pinyin_context_t* context = pinyin_init("data", "data");
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

    // Cleanup
    pinyin_free_instance(instance);
    pinyin_fini(context);

    return 0;
}
