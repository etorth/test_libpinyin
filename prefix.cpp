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


#include <fstream>
#include <iostream>
#include <string>

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include "pinyin.h"

int main(int argc, char * argv[]){
    // Create user.conf if it doesn't exist to avoid warning message
    {
        std::ifstream check_file("data/user.conf");
        if(!check_file){
            std::ofstream create_file("data/user.conf");
        }
    }

    pinyin_context_t * context =
        pinyin_init("data", "data");

    pinyin_option_t options = PINYIN_INCOMPLETE |
        PINYIN_CORRECT_ALL | USE_DIVIDED_TABLE | USE_RESPLIT_TABLE |
        DYNAMIC_ADJUST;
    pinyin_set_options(context, options);

    pinyin_instance_t * instance = pinyin_alloc_instance(context);

    std::string prefix_input;
    std::string line_input;

    while( TRUE ){
        std::cout << "prefix:" << std::flush;

        if (!std::getline(std::cin, prefix_input))
            break;

        std::cout << "pinyin:" << std::flush;

        if (!std::getline(std::cin, line_input))
            break;

        if ( line_input == "quit" )
            break;

        size_t len = pinyin_parse_more_full_pinyins(instance, line_input.c_str());
        pinyin_guess_sentence_with_prefix(instance, prefix_input.c_str());
        guint sort_option = SORT_BY_PHRASE_LENGTH | SORT_BY_FREQUENCY;
        pinyin_guess_candidates(instance, 0, sort_option);

        size_t i = 0;
        for (i = 0; i <= len; ++i) {
            gchar * aux_text = NULL;
            pinyin_get_full_pinyin_auxiliary_text(instance, i, &aux_text);
            std::cout << "auxiliary text:" << aux_text << '\n';
            g_free(aux_text);
        }

        guint num = 0;
        pinyin_get_n_candidate(instance, &num);
        for (i = 0; i < num; ++i) {
            lookup_candidate_t * candidate = NULL;
            pinyin_get_candidate(instance, i, &candidate);

            const char * word = NULL;
            pinyin_get_candidate_string(instance, candidate, &word);

            std::cout << word << '\t';
        }
        std::cout << '\n';

        pinyin_train(instance, 0);
        pinyin_reset(instance);
        pinyin_save(context);
    }

    pinyin_free_instance(instance);

    pinyin_mask_out(context, 0x0, 0x0);
    pinyin_save(context);
    pinyin_fini(context);

    return 0;
}
