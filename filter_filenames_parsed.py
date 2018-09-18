import sys
from collections import OrderedDict
import re

def main():
    all_songs = OrderedDict()
    with open('filenames_parsed', 'r') as f:
        lines = f.readlines()
        for l in lines:
            #skip everything thats not latin
            if 'latin' not in l:
                continue
            split_on_dot = l.split(".")
            split_on_underscore = split_on_dot[0].split("_")
            #We skip those that are just gibberish 
            if len(split_on_underscore) == 1:
                continue
            name = split_on_underscore[:-1]
            all_songs['_'.join(name)] = l
    for k,v in all_songs.items():
        print(v, end='')

if __name__ == '__main__':
    main()
