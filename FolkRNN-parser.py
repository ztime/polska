import sys ,os, argparse, requests, urllib, re
from pprint import pprint

valid_single_tokens = [
        "'",',','/','2','3','4','5','6','7','8','9',':','<','>',
        'A','B','C','D','E','F','G','[',']','a','b','c','d','e',
        'f','g','|']

def main():
    welcome_message = '''
    ####################################
    #       FolkRNN ABC parser         #
    #      Create a Folk-RNN file      #
    #   from a folder with ABC files   #
    ####################################
    '''
    print(welcome_message)
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--folder_path", help="folder with abc files", required=True)
    parser.add_argument("-o", "--output", help="file to save", required=True)
    parser.add_argument("--skip_chords", help="Don't include chords in final product", action='store_true', required=False)
    parser.add_argument("--allow_all_tokens", help="Allow all tokens", action='store_true', required=False)
    parser.add_argument("--print_small_tokens_list", help="Prints the list of alowed one char tokens and then quits", action='store_true', required=False)
    parser.add_argument("--simplify_duplets", help="Clear out more advanced du/tri/plets into (<d> instead of (<d>:<d>:<d>", action='store_true', required=False)
    parser.add_argument("-s", "--save_first_occurance", help="Saves the first occurance to another file, helpful for debugging", required=False)
    args = parser.parse_args()
    if args.print_small_tokens_list:
        print("Here are the list of valid tokens, seperated by spaces:")
        print(" ".join(valid_single_tokens))
        quit()
    print("Creating folk-rnn style %s" % args.output)
    create_folk_rnn_file(args.folder_path, args.output, args.skip_chords, args.allow_all_tokens, args.simplify_duplets, args.save_first_occurance)
    print("Done")

def create_folk_rnn_file(download_dir, output_file, skip_chords, allow_all_tokens, simplify_duplets, save_first_occurance):
    folk_rnn_file = []
    valid_info = ['M', 'L']
    tokens_first_occurance = {}
    tokens_count = {}
    for filename in os.listdir(download_dir):
        file_path = "%s/%s" % (download_dir, filename)
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
            #Skip empty lines
            if len(lines) == 0:
                continue
            lines_with_values, tokens = _filter_song_folk_rnn(lines, valid_info, skip_chords, allow_all_tokens, simplify_duplets)
            if len(lines_with_values) == 0 or len(tokens) == 0:
                continue
            for l in lines_with_values:
                folk_rnn_file.append(l)
            folk_rnn_file.append(' '.join(tokens))
            for t in tokens:
                if save_first_occurance:
                    if t not in tokens_first_occurance:
                        tokens_first_occurance[t] = file_path
                        tokens_count[t] = 0
                    tokens_count[t] += 1
            folk_rnn_file.append('')
    # pprint(tokens_set)
    with open(output_file, 'w') as output:
        for line in folk_rnn_file:
            output.write("%s\n" % line)
    #Save tokens first occurance
    if save_first_occurance:
        sorted_keys = sorted(tokens_first_occurance.keys())
        with open(save_first_occurance, 'w') as output:
            for key in sorted_keys:
                output.write("%s - %s (%d occurances)\n" % (key,tokens_first_occurance[key], tokens_count[key]))
        print("Saved first occurances to %s" % save_first_occurance)
                
#Everything after the first K will be treated as the song and
#concatenaded into one line
def _filter_song_folk_rnn(song_lines, valid_info, skip_chords, allow_all_tokens, simplify_duplets):
    lines_to_return = []
    tokens = []
    currently_parsing_song = False
    for line in song_lines:
        if len(line.strip()) == 0 or line[0] == '%':
            continue
        if not currently_parsing_song:
            s = line.split(":")
            #Check for lyrics in the middle of song and skip it
            if s[0] == 'K' and len(s) == 2:
                key_with_brackets = "[%s]" % line.split('%')[0].replace(" ", "").strip()
                lines_to_return.append(key_with_brackets)
                currently_parsing_song = True
                #Skip to the next line with actual song
                continue
            elif s[0] in valid_info:
                validated_line = line.split('%')[0].replace(" ", "").strip()
                # Special cases for M
                if validated_line[0] == 'M':
                    if validated_line == 'M:C' or validated_line == 'M:c':
                        validated_line = '[M:4/4]'
                    elif validated_line == 'M:C|' or validated_line == 'M:c|':
                        validated_line = '[M:2/2]'
                    # If it's None we just give it 4/4
                    elif validated_line == 'M:None' or validated_line == 'M:none':
                        validated_line = '[M:4/4]'
                if validated_line[0] != '[':
                    validated_line = '[' + validated_line
                if validated_line[-1] != ']':
                    validated_line = validated_line + ']'
                lines_to_return.append(validated_line)
        else:
            #Currently parsing song
            #check if it's a line with lyrics -> skip it
            if line[0] == 'W' or line[0] == 'w':
                continue
            tokens.extend(_filter_song_line(line.strip(), skip_chords, allow_all_tokens, simplify_duplets))
    return lines_to_return, tokens

def _filter_song_line(song_line, skip_chords, allow_all_tokens, simplify_duplets):
    regex_chord = re.compile(r"\"[CDEFGAB](b|bb)?(maj7|maj|min7|min|sus|m)?(1|2|3|4|5|6|7|8|9)?(#)?\"", re.IGNORECASE)
    regex_tempo = re.compile(r"\[?L\:\s?\d+\/\d+\s?\]?", re.IGNORECASE)
    regex_meter = re.compile(r"\[?M\:\s?\d+\/\d+\s?\]?", re.IGNORECASE)
    regex_duplets = re.compile(r"\([2-9]:?[2-9]?:?[2-9]?")
    regex_notedivide = re.compile(r"\/\[1-9]")
    regex_repeat_bar = re.compile(r"::")
    regex_pitch_sharp = re.compile(r"\^[A-Ga-g]")
    regex_pitch_double_sharp = re.compile(r"\^\^[A-Ga-g]")
    regex_pitch_natural = re.compile(r"\=[A-Ga-g]")
    regex_pitch_flat = re.compile(r"_[A-Ga-g]")
    regex_pitch_double_flat = re.compile(r"__[A-Ga-g]")
    #For keys inside a song (key change)
    regex_key = re.compile(r"\[K:\s?[ABCDEFG][#b]?\s?(major|maj|m|minor|min|mixolydian|mix|dorian|dor|phrygian|phr|lydian|lyd|locrian|loc)?\]", re.IGNORECASE)
    regex_accent = re.compile(r"!.*!")
    regex_print_specification = re.compile(r"\"@.+\"")
    regex_inserted_text = re.compile(r"\".+\"")
    regex_repeat_bar_end = re.compile(r":\|")
    regex_repeat_bar_start = re.compile(r"\|:")
    regex_verse_marker = re.compile(r"\[V:.+\]")
    regex_list_tokens = [
            regex_tempo, 
            regex_meter, 
            regex_key, 
            regex_repeat_bar_end, 
            regex_repeat_bar_start, 
            regex_duplets, 
            regex_notedivide,
            regex_repeat_bar,
            regex_pitch_sharp,
            regex_pitch_double_sharp,
            regex_pitch_natural,
            regex_pitch_flat,
            regex_pitch_double_flat,
            ]
    regex_list_ignore = [
            regex_verse_marker, 
            regex_accent, 
            regex_print_specification, 
            regex_inserted_text,
            ]
    if skip_chords:
        regex_list_ignore.append(regex_chord)
    else:
        regex_list_tokens.append(regex_chord)
    ignore_list = '\n \\'
    chars_to_check_regex_for = '"LM[!:|/(^_=abcdefgABCDEFG'
    tokens = []
    char_index = 0
    while char_index < len(song_line):
        char = song_line[char_index]
        #if char is a comment we ignore the rest of the line
        if char == '%':
            break
        if char in ignore_list:
            char_index += 1
            continue
        if char in chars_to_check_regex_for:
            #Check all regexex here
            regex_matched = False
            for regex in regex_list_tokens:
                m = regex.match(song_line[char_index:])
                if m:
                    tok = song_line[char_index:char_index+m.end()]
                    tok = tok.replace(" ", "")
                    if regex == regex_duplets and simplify_duplets:
                        tok = tok[:2]
                    if regex == regex_chord:
                        tok = '"' + tok[1:].capitalize()
                    if regex == regex_meter or regex == regex_tempo:
                        if tok[0] != '[':
                            tok = '[' + tok
                        if tok[-1] != ']':
                            tok = tok + ']'
                    if tok == '::':
                        tokens.append(':|')
                        tok = '|:'
                    tokens.append(tok)
                    char_index = char_index + m.end()
                    regex_matched = True
                    break
            if regex_matched:
                continue
            for regex in regex_list_ignore:
                m = regex.match(song_line[char_index:])
                if m:
                    char_index = char_index + m.end()
                    regex_matched = True
                    break
            if regex_matched:
                continue
        if char in valid_single_tokens or allow_all_tokens:
            tokens.append(char)
        char_index += 1
    return tokens

if __name__ == '__main__':
    main()
