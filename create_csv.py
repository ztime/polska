import sys
import os

def main():
    DIR = 'downloaded_songs'
    csv = []
    valid_info = ['X','T','C','M','L','R','Q','K','notes']
    csv.append(valid_info)
    for filename in os.listdir(DIR):
        file_path = "%s/%s" % (DIR, filename)
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
            if len(lines) == 0:
                continue
            for filtered in filter_song(lines, valid_info):
                csv.append(filtered)
    for c in csv:
        print(','.join(c))

def filter_song(song_lines, valid_info):
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
            continue
        if current_parsing_song:
            songs_in_key[current_parsing_song_key].append(line.strip())
            continue
        if s[0] in valid_info:
            v[s[0]] = s[1].strip()
    for key,song in songs_in_key.items():
        ret = [ r(x,v) for x in valid_info ]
        ret.append(key)
        ret.append(''.join(song))
        yield ret

if __name__ == '__main__':
    main()
