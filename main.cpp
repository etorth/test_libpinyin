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
#include <vector>

const int USER_DICTIONARY_INDEX = 7;
const int USER_PHRASE_FREQUENCY = 100;
const bool REMEMBER_EVERY_INPUT = true;  // Match ibus-libpinyin behavior

// Note: MAX_PHRASE_LENGTH (=16) is defined in novel_types.h (included by pinyin.h)
// This means phrases can be at most 15 characters long

bool read_stdin(const char* prompt, std::string &input)
{
    fprintf(stdout, "%s", prompt);
    fflush(stdout);

    char *buffer = nullptr;
    size_t bufsize = 0;

    ssize_t read = getline(&buffer, &bufsize, stdin);
    if(read == -1){
        return false;
    }

    input = buffer;
    free(buffer);

    while(!input.empty() && input.back() == '\n'){
        input.pop_back();
    }
    return true;
}

void display_candidates(pinyin_instance_t* instance, size_t max)
{
    guint num = 0;
    pinyin_get_n_candidate(instance, &num);

    for(size_t i = 0; i < std::max<size_t>(num, max); ++i){
        lookup_candidate_t* candidate = nullptr;
        pinyin_get_candidate(instance, i, &candidate);

        const char* word = nullptr;
        pinyin_get_candidate_string(instance, candidate, &word);

        lookup_candidate_type_t type;
        pinyin_get_candidate_type(instance, candidate, &type);

        printf("%zu:%s(%d)\t", i, word, static_cast<int>(type));
    }
    printf("\n");
}

void add_to_user_dictionary(pinyin_context_t* context, const std::string& phrase, const std::string& pinyin_input)
{
    if(phrase.empty() || pinyin_input.empty()){
        return;
    }

    // Check phrase length against libpinyin's limit (MAX_PHRASE_LENGTH from novel_types.h)
    glong phrase_length = g_utf8_strlen(phrase.c_str(), -1);
    if(phrase_length >= MAX_PHRASE_LENGTH){
        fprintf(stdout, "Phrase '%s' too long (%ld chars, max %d). Not added to dictionary.\n", phrase.c_str(), phrase_length, MAX_PHRASE_LENGTH - 1);
        return;
    }

    import_iterator_t* iter = pinyin_begin_add_phrases(context, USER_DICTIONARY_INDEX);
    bool added = pinyin_iterator_add_phrase(iter, phrase.c_str(), pinyin_input.c_str(), USER_PHRASE_FREQUENCY);
    pinyin_end_add_phrases(iter);

    fprintf(stdout, "Added phrase '%s' (pinyin: %s): %s\n", phrase.c_str(), pinyin_input.c_str(), added ? "success" : "failed");
}

bool select_candidate(pinyin_instance_t* instance, int chosen, size_t* start_pos, std::string& generated_sentence)
{
    guint num = 0;
    pinyin_get_n_candidate(instance, &num);
    if(chosen < 0 || static_cast<guint>(chosen) >= num){
        fprintf(stderr, "Error: Invalid candidate index %d (valid: 0-%u)\n", chosen, num - 1);
        return false;
    }

    lookup_candidate_t* candidate = nullptr;
    pinyin_get_candidate(instance, chosen, &candidate);

    const char* word = nullptr;
    pinyin_get_candidate_string(instance, candidate, &word);

    lookup_candidate_type_t type;
    pinyin_get_candidate_type(instance, candidate, &type);

    if(type == NBEST_MATCH_CANDIDATE){
        // NBEST match candidate represents a full generated_sentence match
        // According to pinyin.cpp, choose from position 0 and it returns matrix.size()-1
        *start_pos = pinyin_choose_candidate(instance, 0, candidate);

        // Get the nbest index for training
        guint8 index = 0;
        pinyin_get_candidate_nbest_index(instance, candidate, &index);

        // Train if not the top choice (ibus-libpinyin pattern)
        if(index != 0){
            pinyin_train(instance, index);
        }

        // Get the full generated_sentence using the nbest index
        gchar* full_sentence = nullptr;
        pinyin_get_sentence(instance, index, &full_sentence);

        if(full_sentence){
            generated_sentence = full_sentence;
            g_free(full_sentence);
        }
    }
    else if(type == LONGER_CANDIDATE){
        // LONGER candidate - starts from position 0, covers more of input
        // According to pinyin.cpp: choose from 0, trains uni-gram internally
        // Do NOT call pinyin_train(instance, 0) later for LONGER candidates
        *start_pos = pinyin_choose_candidate(instance, 0, candidate);
        generated_sentence = word;
    }
    else {
        // Normal/phrase candidate - incremental selection
        generated_sentence += word;

        // Choose candidate and get new position
        *start_pos = pinyin_choose_candidate(instance, *start_pos, candidate);

        // Guess generated_sentence for better next predictions (ibus-libpinyin pattern)
        pinyin_guess_sentence(instance);
    }

    fprintf(stdout, "generated_sentence:%s\n", generated_sentence.c_str());
    fflush(stdout);

    return true;
}

std::pair<std::string, bool> process_pinyin_input(pinyin_instance_t* instance, const std::string &prefix_input, const std::string &pinyin_input)
{
    bool skip_train = false;
    std::string generated_sentence;

    for(size_t start = 0; start < pinyin_input.size();){
        pinyin_guess_candidates(instance, start, SORT_BY_PHRASE_LENGTH_AND_PINYIN_LENGTH_AND_FREQUENCY);
        display_candidates(instance, 20); // print first 20 candidates

        std::string chosen_str;
        if(!read_stdin("choose:", chosen_str)){
            break;
        }

        const int chosen = std::stoi(chosen_str);

        guint num = 0;
        pinyin_get_n_candidate(instance, &num);

        if(chosen >= 0 && static_cast<guint>(chosen) < num){
            lookup_candidate_t* candidate = nullptr;
            pinyin_get_candidate(instance, chosen, &candidate);

            lookup_candidate_type_t type;
            pinyin_get_candidate_type(instance, candidate, &type);

            // LONGER or NBEST candidates selected after position 0 cause training conflicts
            // These candidates try to match from the beginning but constraints are already set, skip training for these cases
            if((type == LONGER_CANDIDATE || type == NBEST_MATCH_CANDIDATE) && start > 0){
                skip_train = true;
            }
        }

        if(!select_candidate(instance, chosen, &start, generated_sentence)){
            continue;
        }
    }

    return std::make_pair(generated_sentence, skip_train);
}

bool is_input_complete_pinyin(pinyin_instance_t* instance)
{
    size_t n_pinyin = pinyin_get_parsed_input_length(instance);
    for (size_t i = 0; i < n_pinyin; ++i){
        ChewingKey* key = nullptr;
        if(pinyin_get_pinyin_key(instance, i, &key) && key){
            if(pinyin_get_pinyin_is_incomplete(instance, key)){
                return false;
            }
        }
    }
    return true;
}

void train_and_save(pinyin_context_t* context, pinyin_instance_t* instance,
                   const std::string& prefix_input,
                   const std::string& pinyin_input,
                   const std::string& generated_sentence, bool skip_train)
{
    if(generated_sentence.empty()){
        return;
    }

    // LONGER/NBEST candidates selected after position 0 are special cases
    // They try to re-match from beginning which conflicts with existing constraints
    // Do NOT call train() or remember_user_input() for them
    if(!skip_train){
        // Train bigram model with user selections
        pinyin_train(instance, 0);

        // Remember user input - matches ibus-libpinyin behavior
        if(REMEMBER_EVERY_INPUT){
            pinyin_remember_user_input(instance, generated_sentence.c_str(), -1);
        }
    }

    // Add complete phrases to user dictionary for direct lookup
    // Check if input is complete pinyin (before selections modify state)
    if(is_input_complete_pinyin(instance)){
        add_to_user_dictionary(context, generated_sentence, pinyin_input);
    }
    else {
        fprintf(stdout, "Skipped adding phrase '%s' - incomplete pinyin input\n", generated_sentence.c_str());
    }

    // Log what we're learning
    if(!prefix_input.empty()){
        fprintf(stdout, "Learning: '%s' → '%s'\n", prefix_input.c_str(), generated_sentence.c_str());
    }

    // Save to persistent storage
    pinyin_save(context);
}

int main(int argc, char* argv[])
{
    if(FILE* check_file = fopen("data/user.conf", "r")){
        fclose(check_file);
    }
    else if(FILE* create_file = fopen("data/user.conf", "w")){
        fclose(create_file);
    }

    pinyin_context_t* context = pinyin_init("data", "data");
    if(!context){
        fprintf(stderr, "Error: Failed to initialize pinyin context\n");
        return 1;
    }

    pinyin_option_t options = PINYIN_INCOMPLETE | PINYIN_CORRECT_ALL | USE_DIVIDED_TABLE | USE_RESPLIT_TABLE | DYNAMIC_ADJUST;
    pinyin_set_options(context, options);

    pinyin_instance_t* instance = pinyin_alloc_instance(context);
    if(!instance){
        fprintf(stderr, "Error: Failed to allocate pinyin instance\n");
        pinyin_fini(context);
        return 1;
    }

    std::string prefix_input;
    std::string pinyin_input;

    while(true){
        if(!read_stdin("prefix(Chinese):", prefix_input)) break;
        if(prefix_input == "quit") break;

        if(!read_stdin("pinyin:", pinyin_input)) break;
        if(pinyin_input == "quit") break;

        pinyin_parse_more_full_pinyins(instance, pinyin_input.c_str());

        const auto [generated_sentence, skip_train] = process_pinyin_input(instance, prefix_input, pinyin_input);
        train_and_save(context, instance, prefix_input, pinyin_input, generated_sentence, skip_train);

        pinyin_reset(instance);
    }

    pinyin_save(context);
    pinyin_free_instance(instance);

    pinyin_mask_out(context, 0x0, 0x0);
    pinyin_save(context);
    pinyin_fini(context);

    return 0;
}
