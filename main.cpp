/*
 *  libpinyin
 *  Library to deal with pinyin.
 *
 *  Copyright (C) 2011 Peng Wu <alexepico@gmail.com>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "pinyin.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>

const int USER_DICTIONARY_INDEX = 7;
const int USER_PHRASE_FREQUENCY = 100;

// Read a line from stdin and remove trailing newline
bool read_line(char** buffer, size_t* bufsize, const char* prompt) {
    fprintf(stdout, "%s", prompt);
    fflush(stdout);

    ssize_t read = getline(buffer, bufsize, stdin);
    if (read == -1) {
        return false;
    }

    size_t len = strlen(*buffer);
    if (len > 0 && (*buffer)[len - 1] == '\n') {
        (*buffer)[len - 1] = '\0';
    }

    return true;
}

// Display candidates for user selection
void display_candidates(pinyin_instance_t* instance) {
    guint num = 0;
    pinyin_get_n_candidate(instance, &num);

    for (size_t i = 0; i < num; ++i) {
        lookup_candidate_t* candidate = NULL;
        pinyin_get_candidate(instance, i, &candidate);

        const char* word = NULL;
        pinyin_get_candidate_string(instance, candidate, &word);

        lookup_candidate_type_t type;
        pinyin_get_candidate_type(instance, candidate, &type);

        printf("%zu:%s(%d)\t", i, word, (int)type);
    }
    printf("\n");
}

// Add phrase to user dictionary
void add_to_user_dictionary(pinyin_context_t* context, pinyin_instance_t* instance,
                            const std::string& phrase, const std::string& pinyin_str,
                            bool is_complete) {
    if (phrase.empty() || pinyin_str.empty()) {
        return;
    }

    if (!is_complete) {
        fprintf(stdout, "Skipped adding phrase '%s' - incomplete pinyin input\n",
                phrase.c_str());
        return;
    }

    import_iterator_t* iter = pinyin_begin_add_phrases(context, USER_DICTIONARY_INDEX);
    bool added = pinyin_iterator_add_phrase(iter, phrase.c_str(),
                                           pinyin_str.c_str(), USER_PHRASE_FREQUENCY);
    pinyin_end_add_phrases(iter);

    fprintf(stdout, "Added phrase '%s' (pinyin: %s): %s\n",
            phrase.c_str(), pinyin_str.c_str(),
            added ? "success" : "failed");
}

// Process one candidate selection step
bool select_candidate(pinyin_instance_t* instance, char* input_buf,
                     size_t* start_pos, std::string& sentence) {
    int chosen = atoi(input_buf);

    lookup_candidate_t* candidate = NULL;
    pinyin_get_candidate(instance, chosen, &candidate);

    const char* word = NULL;
    pinyin_get_candidate_string(instance, candidate, &word);

    lookup_candidate_type_t type;
    pinyin_get_candidate_type(instance, candidate, &type);

    if (type == NBEST_MATCH_CANDIDATE) {
        sentence = word;
    } else {
        sentence += word;
    }

    fprintf(stdout, "sentence:%s\n", sentence.c_str());
    fflush(stdout);

    *start_pos = pinyin_choose_candidate(instance, *start_pos, candidate);
    return true;
}

// Main input loop for selecting candidates
std::string process_pinyin_input(pinyin_instance_t* instance, const char* pinyin_input,
                                 char** buffer, size_t* bufsize) {
    auto sort_option = SORT_BY_PHRASE_LENGTH_AND_PINYIN_LENGTH_AND_FREQUENCY;

    size_t start = 0;
    std::string generated_sentence;

    while (start < strlen(pinyin_input)) {
        pinyin_guess_candidates(instance, start, sort_option);
        display_candidates(instance);

        if (!read_line(buffer, bufsize, "choose:")) {
            break;
        }

        select_candidate(instance, *buffer, &start, generated_sentence);
    }

    return generated_sentence;
}

// Learn from user input and save to dictionary
void learn_and_save(pinyin_context_t* context, pinyin_instance_t* instance,
                   const std::string& sentence, const std::string& pinyin_str,
                   bool is_complete, const std::string& previous_phrase) {
    if (sentence.empty()) {
        return;
    }

    // Train bigram model with user selections
    // This learns phrase transitions: after "我是", "你爸" becomes more likely
    pinyin_train(instance, 0);

    // Add phrase to user dictionary (only if pinyin is complete)
    add_to_user_dictionary(context, instance, sentence, pinyin_str, is_complete);

    // Log the bigram relationship being learned
    // Over time, libpinyin will learn that after the previous_phrase,
    // this sentence is more likely to appear
    if (!previous_phrase.empty() && !sentence.empty()) {
        fprintf(stdout, "Learning bigram: '%s' → '%s' (builds over time)\n",
                previous_phrase.c_str(), sentence.c_str());
    }

    // Save to persistent storage
    pinyin_save(context);
}

int main(int argc, char* argv[]) {
    // Create user.conf if it doesn't exist to avoid warning message
    FILE* check_file = fopen("data/user.conf", "r");
    if (!check_file) {
        FILE* create_file = fopen("data/user.conf", "w");
        if (create_file) {
            fclose(create_file);
        }
    } else {
        fclose(check_file);
    }

    // Initialize libpinyin
    pinyin_context_t* context = pinyin_init("data", "data");

    pinyin_option_t options = PINYIN_INCOMPLETE | PINYIN_CORRECT_ALL |
                             USE_DIVIDED_TABLE | USE_RESPLIT_TABLE | DYNAMIC_ADJUST;
    pinyin_set_options(context, options);

    pinyin_instance_t* instance = pinyin_alloc_instance(context);

    // Input buffers
    char* prefixbuf = NULL;
    size_t prefixsize = 0;
    char* linebuf = NULL;
    size_t linesize = 0;

    // Context for bigram learning
    std::string previous_phrase;

    // Main input loop
    while (true) {
        // Read prefix (previous context)
        if (!read_line(&prefixbuf, &prefixsize, "prefix (Chinese chars):")) {
            break;
        }
        previous_phrase = prefixbuf;

        // Read pinyin input
        if (!read_line(&linebuf, &linesize, "pinyin:")) {
            break;
        }

        if (strcmp(linebuf, "quit") == 0) {
            break;
        }

        // Parse pinyin input
        pinyin_parse_more_full_pinyins(instance, linebuf);

        // Check if input is complete pinyin (before selections modify state)
        bool is_complete = true;
        size_t n_pinyin = pinyin_get_parsed_input_length(instance);
        for (size_t i = 0; i < n_pinyin; ++i) {
            ChewingKey* key = NULL;
            if (pinyin_get_pinyin_key(instance, i, &key) && key) {
                if (pinyin_get_pinyin_is_incomplete(instance, key)) {
                    is_complete = false;
                    break;
                }
            }
        }

        // Process user selections
        std::string generated_sentence = process_pinyin_input(instance, linebuf,
                                                             &prefixbuf, &prefixsize);

        // Learn from selections and save (use raw input as pinyin string)
        learn_and_save(context, instance, generated_sentence, linebuf,
                      is_complete, previous_phrase);

        // Update context for next iteration
        previous_phrase = generated_sentence;

        // Reset instance for next input
        pinyin_reset(instance);
    }

    // Cleanup
    pinyin_save(context);
    pinyin_free_instance(instance);

    pinyin_mask_out(context, 0x0, 0x0);
    pinyin_save(context);
    pinyin_fini(context);

    free(prefixbuf);
    free(linebuf);
    return 0;
}
