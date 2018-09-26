import sys ,os, argparse, requests, urllib, re

def main():
    welcome_message = '''
    ####################################
    #       FolkRNN ABC parser         #
    # Create a CSV or Folk-RNN file    #
    # from a folder with ABC files     #
    ####################################
    '''
    print(welcome_message)
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--folder_path", help="folder with abc files", required=True)
    parser.add_argument("-o", "--output", help="file to save", required=True)
    parser.add_argument("-s", "--style", help="What style to save the file as", choices=['folk-rnn', 'csv'], required=True)
    parser.add_argument("--skip_chords", help="Don't include chords in final product", action='store_true', required=False)
    parser.add_argument("--allow_all_tokens", help="Allow all tokens (just not the ~48 from original folk-rnn", action='store_true', required=False)
    args = parser.parse_args()
    if args.style == 'folk-rnn':
        print("Creating folk-rnn style %s" % args.output)
        create_folk_rnn_file(args.folder_path, args.output, args.skip_chords, args.allow_all_tokens)
    else:
        print("Warning! Not really maintaining the csv mode so results might not be correct!")
        print("Creating csv file %s" % args.output)
        create_csv_file(args.folder_path, args.output)
    print("Done")

def create_folk_rnn_file(download_dir, output_file, skip_chords, allow_all_tokens):
    folk_rnn_file = []
    valid_info = ['M', 'L']
    for filename in os.listdir(download_dir):
        file_path = "%s/%s" % (download_dir, filename)
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
            #Skip empty lines
            if len(lines) == 0:
                continue
            lines_with_values, tokens = _filter_song_folk_rnn(lines, valid_info, skip_chords, allow_all_tokens)
            if len(lines_with_values) == 0 or len(tokens) == 0:
                continue
            for l in lines_with_values:
                folk_rnn_file.append(l)
            folk_rnn_file.append(' '.join(tokens))
            folk_rnn_file.append('')
    with open(output_file, 'w') as output:
        for line in folk_rnn_file:
            output.write("%s\n" % line)
                
#Everything after the first K will be treated as the song and
#concatenaded into one line
def _filter_song_folk_rnn(song_lines, valid_info, skip_chords, allow_all_tokens):
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
                validated_line = line.split('%')[0].replace(" ", "")
                lines_to_return.append(validated_line.strip())
        else:
            #Currently parsing song
            #check if it's a line with lyrics -> skip it
            if line[0] == 'W' or line[0] == 'w':
                continue
            tokens.extend(_filter_song_line(line.strip(), skip_chords, allow_all_tokens))
    return lines_to_return, tokens

def _filter_song_line(song_line, skip_chords, allow_all_tokens):
    regex_chord = re.compile(r"\"[CDEFGAB](b|bb)?(maj7|maj|min7|min|sus|m)?(1|2|3|4|5|6|7|8|9)?(#)?\"", re.IGNORECASE)
    regex_tempo = re.compile(r"\[?L\:\s?\d+\/\d+\s?\]?", re.IGNORECASE)
    regex_meter = re.compile(r"\[?M\:\s?\d+\/\d+\s?\]?", re.IGNORECASE)
    #For keys inside a song (key change)
    regex_key = re.compile(r"\[K:\s?[ABCDEFG][#b]?\s?(major|maj|m|minor|min|mixolydian|mix|dorian|dor|phrygian|phr|lydian|lyd|locrian|loc)?\]", re.IGNORECASE)
    regex_accent = re.compile(r"!.*!")
    regex_print_specification = re.compile(r"\"@.+\"")
    regex_inserted_text = re.compile(r"\".+\"")
    regex_repeat_bar_end = re.compile(r":\|")
    regex_repeat_bar_start = re.compile(r"\|:")
    regex_verse_marker = re.compile(r"\[V:.+\]")
    regex_list_tokens = [regex_tempo, regex_meter, regex_key, regex_repeat_bar_end, regex_repeat_bar_start]
    regex_list_ignore = [regex_verse_marker, regex_accent, regex_print_specification, regex_inserted_text]
    if skip_chords:
        regex_list_ignore.append(regex_chord)
    else:
        regex_list_tokens.append(regex_chord)
    ignore_list = '\n \\'
    #These are all the tokens from the original dataset folk-rnn
    valid_single_tokens = ["'",'(',',','/','1','2','3','4','5','6','7','8','9',':','<','=','>','A','B','C','D','E','F','G','K','M','[',']','^','_','a','b','c','d','e','f','g','i','j','m','n','o','r','x','z','|']

    chars_to_check_regex_for = '"LM[!:|'
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
            for regex in regex_list_ignore:
                m = regex.match(song_line[char_index:])
                if m:
                    char_index = char_index + m.end()
                    regex_matched = True
                    break
            if regex_matched:
                continue
            for regex in regex_list_tokens:
                m = regex.match(song_line[char_index:])
                if m:
                    tok = song_line[char_index:char_index+m.end()]
                    tok = tok.replace(" ", "")
                    tokens.append(tok)
                    char_index = char_index + m.end()
                    regex_matched = True
                    break
            if regex_matched:
                continue
        if char in valid_single_tokens or allow_all_tokens:
            tokens.append(char)
        char_index += 1
    return tokens

def create_csv_file(download_dir, output_file):
    csv = []
    #first part of csv file is description
    valid_info = ['X','T','C','M','L','R','Q','K','notes']
    csv.append(valid_info)
    for filename in os.listdir(download_dir):
        file_path = "%s/%s" % (download_dir, filename)
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
            #skip empty files
            if len(lines) == 0:
                continue
            for filtered in _filter_song_csv(lines, valid_info):
                csv.append(filtered)
    with open(output_file, 'w') as f:
        for c in csv:
            f.write(','.join(c))
            f.write('\n')
    print("Written to %s" % output_file)

def _filter_song_csv(song_lines, valid_info):
    #Function to reduce linesize
    def r(key, hay):
        return hay.get(key, "")
    v = {}
    songs_in_key = {}
    current_parsing_song = False
    current_parsing_song_key = None
    for line in song_lines:
        if len(line.strip()) == 0:
            continue
        s = line.split(":")
        if s[0] == 'K' and len(s) == 2:
            current_parsing_song_key = s[1].strip()
            current_parsing_song = True
            songs_in_key[current_parsing_song_key] = []
            #Skip to the next line with actual song
            continue
        if current_parsing_song:
            songs_in_key[current_parsing_song_key].append(line.strip())
            #more song lines
            continue
        if s[0] in valid_info:
            v[s[0]] = s[1].strip()
    #One file can contain several keys
    for key,song in songs_in_key.items():
        ret = [ r(x,v) for x in valid_info ]
        ret.append(key)
        ret.append(''.join(song))
        yield ret

if __name__ == '__main__':
    main()
