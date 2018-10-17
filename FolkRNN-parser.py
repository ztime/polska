import sys
import os
import argparse
import re
from pprint import pprint

#We need some global variabels for when parsing tokens
valid_metrics = ['[M:4/4]', '[M:2/2]', '[M:3/4]']
valid_metrics_translations = {
        '[M:C]' : '[M:4/4]',
        '[M:C|]': '[M:2/2]',
        '[M:3/8+3/8+2/8]' : '[M:7/8]',
        }
valid_lengths = ['[L:1/8]', '[L:1/4]', '[L:1/16]']
valid_lengths_translations = {
        '[L:2/8]' : '[L:1/4]'
        }
#Keys
valid_keys = []
valid_keys_translations = {
        '[K:A]' : '[K:AMaj]', 
        '[K:B]' : '[K:BMaj]', 
        '[K:C]' : '[K:CMaj]', 
        '[K:D]' : '[K:DMaj]', 
        '[K:E]' : '[K:EMaj]', 
        '[K:F]' : '[K:FMaj]', 
        '[K:G]' : '[K:GMaj]', 
        '[K:Ab]' : '[K:AbMaj]', 
        '[K:Bb]' : '[K:BbMaj]', 
        '[K:Cb]' : '[K:CbMaj]', 
        '[K:Db]' : '[K:DbMaj]', 
        '[K:Eb]' : '[K:EbMaj]', 
        '[K:Fb]' : '[K:FbMaj]', 
        '[K:Gb]' : '[K:GbMaj]', 
        }
# Dirty global variable
g_keep_duplets = False

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
    parser.add_argument(
            "-f",
            "--folder_path",
            help="Folder with abc files",
            required=True)
    parser.add_argument(
            "-o",
            "--output",
            help="File to save",
            required=True)
    parser.add_argument(
            "--keep_duplets",
            help="Don't simplify duplets",
            action='store_true')
    # parser.add_argument(
            # "--keep-chords",
            # help="Don't remove chords",
            # action='store_true')
    parser.add_argument(
            "--save_filename",
            help="Save filename as T field for easier debugging",
            action='store_true')
    args = parser.parse_args()
    if args.keep_duplets:
        g_keep_duplets = True

    file_list = get_all_filenames(args.folder_path)
    # with open(args.output, 'w') as f:
    for filename in file_list:
        print("-------------")
        print(filename)
        song_head, song_body = parse_file(filename)
        for song in song_body:
            tokenized_song = tokenize_song(song)
            pprint(tokenized_song)
            quit()

# Takes a string that represents a song and tokenizes it
# with a space between each token
def tokenize_song(song):
    # First we define a few regexes 
    re_key = re.compile(r"\[K:\s?[ABCDEFG][#b]?\s?(major|maj|m|minor|min|mixolydian|mix|dorian|dor|phrygian|phr|lydian|lyd|locrian|loc)?\]", re.IGNORECASE)
    re_tempo = re.compile(r"\[?L\:\s?\d+\/\d+\s?\]?", re.IGNORECASE)
    re_meter = re.compile(r"\[?M\:\s?\d+\/\d+\s?\]?", re.IGNORECASE)
    re_duplets = re.compile(r"\([2-9]:?[2-9]?:?[2-9]?")
    re_note = re.compile(r"\^{0,2}\_{0,2}=?,?[A-Ga-g]'?,?")
    re_length = re.compile(r"[1-9]{0,2}\/{0,2}[1-9]{1,2}")
    re_rest = re.compile(r"[z]\d?")
    re_repeat = re.compile(r"\|\[?\d")
    re_bar = re.compile(r":?\|:?")
    re_durations = re.compile(r"<{1,2}|>{1,2}")
    re_grouping = re.compile(r"[\[\]]")
    #Regex should be added in prority order since if one matches
    #it will stop
    regex_list = [
            re_key,
            re_tempo,
            re_meter,
            re_duplets,
            re_note,
            re_repeat,
            re_rest,
            re_bar,
            re_grouping,
            re_length,
            ]
    #Actual parsing
    song = filter_song_string(song)
    tokens = []
    char_index = 0
    print(song)
    while char_index < len(song):
        print("Char at %d: %s" % (char_index, song[char_index:char_index+1]))
        for regex in regex_list:
            print("X")
            match_token = regex.match(song[char_index:])
            if  match_token is None:
                char_index += 1
                continue
            # Something matched
            print("Match start:%d end:%d" % (match_token.start(), match_token.end()))
            regex_matched = True
            token = song[char_index:match_token.end()]
            # We might have an empty token bc of length
            pprint(match_token)
            print("Token:'%s'" % token)
            #We need to handle some tokens individually
            #We allow each if to modify the token variable
            #and then add it to the token list
            if regex == re_key:
                token = _filter_keys(token)
            elif regex == re_duplets:
                if not g_keep_duplets:
                    token = token[:2]
            elif regex == re_length:
                token = _filter_length(token)
            elif regex == re_meter:
                token = _filter_meter(token)
            elif regex == re_repeat:
                token = _filter_repeat(token)
            char_index = char_index + match_token.end()
            tokens.append(token)
            #We are finished, next token
            break
    return tokens

# Uses regexes to remove/replace 
# strings inside the song string and returns the filtered string
def filter_song_string(song):
    #First we remove anything unwanted
    re_remove_unwanted = [
            re.compile(r"!.*?!"), # Accents
            re.compile(r"\"@.+?\""), # Print specifications
            re.compile(r"\".+?\""), # Inserted text
            ]
    for regex in re_remove_unwanted:
        song, _ = re.subn(regex, '', song)
    # Now we replace any chars that are needed
    # The keys are regex to match and value is what to replace with
    re_replace = {
            # All different repeat signs 
            re.compile(r":\s?:|:\s?\|\s?:|:\s?\|\s?\|\s?:") : ':| |:',
            # Different bar signs (fat bar etc)
            re.compile(r"\]\s?\||\|\||\[\s?\||\|\]") : '|',
            }
    for regex, replacement in re_replace.items():
        song, _ = re.subn(regex, replacement, song)
    return song

# Takes a file and parses it into one or more songs 
# depending on if there are more voices in it
def parse_file(filename):
    lines_in_file = open(filename, 'r').readlines()
    song_head, song_body = filter_head_body(lines_in_file)
    return song_head, song_body

# Scans a song and returns a a tuple with
# ({dict with metainformation}, [voice1, voice2...])
def filter_head_body(lines_in_file):
    reached_song_body = False
    lines_song_head = []
    lines_song_body = []
    #First we filter out the head from the body
    for line in lines_in_file:
        #Check for comments and remove them if found
        if line.find('%') > -1:
            line = line[:line.find('%')]
        if not reached_song_body:
            lines_song_head.append(line)
            #Check if we are at the last line before song body
            #which has the key for the songs
            if line.split(':')[0].strip().upper() == 'K':
                reached_song_body = True
        else:
            lines_song_body.append(line)
    song_head = process_song_head(lines_song_head)
    song_body = process_song_body(lines_song_body)
    return song_head, song_body

# Filters song body into a list, where each entry in the list
# is a voice in the song
def process_song_body(lines_song_body):
    # First we check if there even is a V: in there
    if ''.join(lines_song_body).find('V:') < 0:
        # No voices
        return [''.join(lines_song_body)]
    # different voices can either be written as
    # V:<d> on a single line or [V:<d>] on the same line
    # this matches that plus optional whitespace
    # saves the digit as the first match
    re_voice = re.compile(r"\[?\s?[Vv]\s?:\s?(\d+)\s?\]?")
    voices = {}
    current_voice = None
    for line in lines_song_body:
        voice_match = re_voice.search(line)
        if voice_match:
            # The first group is the voice digit
            current_voice = voice_match.group(1)
            # Filter the line and remove the V tag
            line = line[:voice_match.start()] + line[voice_match.end():]
        if current_voice not in voices:
            voices[current_voice] = ''
        voices[current_voice] += line
    return voices.values()
    
# Scans a song head and returns a dict with the meta information
# if it finds several of the same tag, it appends that string onto 
# the exisiting one
def process_song_head(lines_song_head):
    head = {}
    for line in lines_song_head:
        split_line = line.split(':')
        meta_tag = split_line[0].strip()
        meta_info = split_line[-1].strip()
        if meta_tag not in head:
            head[meta_tag] = meta_info
        else:
            head[meta_tag] += ' ' + meta_info
    return head

# Scans a folder for all files with abc in it and returns a 
# list of full paths
def get_all_filenames(folder):
    file_list = []
    for filename in os.listdir(folder):
        if 'abc' in filename:
            file_list.append("%s/%s" % (folder, filename))
    return file_list

#### Functions for filtering ####
def _filter_keys(key_string):
    #Check the string first 
    if key_string[0] != '[':
        key_string = '[' + key_string
    if key_string[-1] != ']':
        key_string = key_string + ']'
    #Special for keys 
    key_string = _filter_keys_tone(key_string)
    #We always have a tone in the beginning that suppose to be uppercase
    if len(key_string) >= 4: # [K:<LETTER>]> 4
        key_string = key_string[:3] + key_string[3].upper() + key_string[4:]
    original_key_string = key_string
    if key_string in valid_keys:
        #we already checked this one, its fine
        return key_string
    if key_string in valid_keys_translations:
        return valid_keys_translations[key_string]
    #now to the checking part
    print("%s was not found in currently valid keys, add it or change it?" % key_string)
    print("DEBUG: ORIGINAL: %s" % original_key_string)
    print("Needs to be entered with brackets and all e.g [K:E] AND THERE IS NO UNDO")
    print("Keys follow this format [K:<NOTE>b?<THREE LETTERS FOR SCALE OR 'Min' 'Maj'>]")
    print("Press enter to keep the string as is, or input a new one to be added")
    new_key_string = input("%s =>" % key_string)
    if new_key_string != '':
        key_string = new_key_string
    valid_keys_translations[original_key_string] = key_string
    valid_keys.append(key_string)
    return key_string

def _filter_keys_tone(key_string):
    #Regexes for different modes
    #Regex and next line is replacement
    #Longest expressions first! and minor must be last because it has
    # 'm' which is short as hell
    regex_modes = {}
    #major is the same as Ionian
    r_major = re.compile(r"(major|maj|ionian|ion)", re.IGNORECASE)
    regex_modes[r_major] = 'Maj'
    #Mixolydian 
    r_mix = re.compile(r"(mixolydian|mix)", re.IGNORECASE)
    regex_modes[r_mix] = 'Mix'
    #Dorian
    r_dorian = re.compile(r"(dorian|dor)", re.IGNORECASE)
    regex_modes[r_dorian] = 'Dor'
    #Phrygian
    r_phyr = re.compile(r"(phrygian|phr)", re.IGNORECASE)
    regex_modes[r_phyr] = 'Phr'
    #Lydian
    r_lydian = re.compile(r"(lydian|lyd)", re.IGNORECASE)
    regex_modes[r_lydian] = 'Lyd'
    #Locrian
    r_locrian = re.compile(r"(locrian|loc)", re.IGNORECASE)
    regex_modes[r_locrian] = 'Loc'
    #minor is the same as Aeolian
    r_minor = re.compile(r"(aeolian|minor|aeo|min|m)", re.IGNORECASE)
    regex_modes[r_minor] = 'Min'
    for pattern, replacement in regex_modes.items():
        key_string, count_replaced = re.subn(pattern, replacement, key_string)
        if count_replaced > 0:
            break
    return key_string

def _filter_metric(metric_string):
    #Check the string first 
    if metric_string[0] != '[':
        metric_string = '[' + metric_string
    if metric_string[-1] != ']':
        metric_string = metric_string + ']'
    original_metric_string = metric_string
    if metric_string in valid_metrics:
        #we already checked this one, its fine
        return metric_string
    #Check if we already translated it
    if metric_string in valid_metrics_translations:
        return valid_metrics_translations[metric_string]
    #now to the checking part
    print("%s was not found in currently valid metrics, add it or change it?" % metric_string)
    print("Needs to be entered with brackets and all e.g [M:1/4] AND THERE IS NO UNDO")
    print("Press enter to keep the string as is, or input a new one to be added")
    new_metric_string = input("%s =>" % metric_string)
    #just add as is and move on
    if new_metric_string != '':
        metric_string = new_metric_string
    valid_metrics_translations[original_metric_string] = metric_string
    valid_metrics.append(metric_string)
    return metric_string

def _filter_length(length_string):
    #Check the string first 
    if length_string[0] != '[':
        length_string = '[' + length_string
    if length_string[-1] != ']':
        length_string = length_string + ']'
    original_length_string = length_string
    if length_string in valid_lengths:
        #we already checked this one, its fine
        return length_string
    if length_string in valid_lengths_translations:
        return valid_lengths_translations[length_string]
    #now to the checking part
    print("%s was not found in currently valid lengths, add it or change it?" % length_string)
    print("Needs to be entered with brackets and all e.g [L:1/4] AND THERE IS NO UNDO")
    print("Press enter to keep the string as is, or input a new one to be added")
    new_length_string = input("%s =>" % length_string)
    if new_length_string != '':
        length_string = new_length_string
    valid_lengths_translations[original_length_string] = length_string
    valid_lengths.append(length_string)
    return length_string

def _filter_repeat(repeat_string):
    return repeat_string

if __name__=='__main__':
    main()
