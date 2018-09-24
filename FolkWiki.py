import sys, os, re, argparse, requests, urllib, re

def main():
    welcome_message = '''
    ####################################
    #       FolkWiki downloader        #
    # Downloads songs from folkwiki.se #
    # and creates an csv file from all #
    #           of them.               #
    ####################################
    '''
    print(welcome_message)
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="the url with listing of all songs")
    parser.add_argument("-f", "--filter", help="must be in the filename of the song")
    parser.add_argument("-d","--download_path", help="folder to download songs to", required=True)
    parser.add_argument("-o", "--output", help="file to save", required=True)
    parser.add_argument("--folk_rnn_style", help="Save as folk-rnn style instead of csv", action='store_true')
    parser.add_argument("--skip_download", help="Skips downloading of songs and just creates file from download_path", action='store_true')
    args = parser.parse_args()
    #get all songs
    if args.skip_download:
        print("Skipping downloads and just parsing files in %s" % args.download_path)
    else:
        print("Checking %s for songs..." % args.url)
        songs_to_download = get_song_list(args.url, args.filter)
        print("Found %d songs at %s" % (len(songs_to_download), args.url))
        if not os.path.isdir('./%s' % args.download_path):
            create_dir = input("Could not find directory %s, create it? [Y/n]" % args.download_path)
            if create_dir == 'y' or create_dir == 'Y':
                os.makedirs('./%s' % args.download_path)
            else:
                print("Aborting bc no download directory")
                quit()
        print("Starting download to: %s" % args.download_path)
        download_all_songs(songs_to_download, args.download_path)
        if os.path.isfile('./%s' % args.output):
            overwrite_file = input("File %s already exists, overwrite it?[Y/n]" % args.output)
            if overwrite_file != 'Y' and overwrite_file != 'y':
                print("Aborting bc file already exists.")
                quit()
    if args.folk_rnn_style:
        print("Creating folk-rnn style %s" % args.output)
        create_folk_rnn_file(args.download_path, args.output)
    else:
        print("Creating csv file %s" % args.output)
        create_csv_file(args.download_path, args.output)
    print("Done")

def create_folk_rnn_file(download_dir, output_file):
    folk_rnn_file = []
    valid_info = ['T', 'M', 'L']
    for filename in os.listdir(download_dir):
        file_path = "%s/%s" % (download_dir, filename)
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
            #Skip empty lines
            if len(lines) == 0:
                continue
            for filtered in _filter_song(lines, valid_info):
                # print("T:%s" % filtered[0])
                # print("L:%s" % filtered[2])
                # print("M:%s" % filtered[1])
                # print("K:%s" % filtered[3])
                # print(filtered[4].replace(" ", ""))
                regex_chord = r"\"[CDEFGAB](b|bb)?(maj7|maj|min7|min|sus|m)?(1|2|3|4|5|6|7|8|9)?(#)?\""
                m = re.search(regex_chord, filtered[4].replace(" ", ""))
                if m is not None:
                    print(m)
                



def _filter_song_folk_rnn(song_lines, valid_info):
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
            for filtered in _filter_song(lines, valid_info):
                csv.append(filtered)
    with open(output_file, 'w') as f:
        for c in csv:
            f.write(','.join(c))
            f.write('\n')
    print("Written to %s" % output_file)

def _filter_song(song_lines, valid_info):
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

def download_all_songs(song_list, download_dir):
    count = 1
    for song in song_list:
        print('\rDownloading song %d/%d...' % (count, len(song_list)), end="")
        song_without_url = song.split("/")[-1]
        file_path = '%s/%s' % (download_dir, song_without_url)
        urllib.request.urlretrieve(song, file_path)
        count += 1
    print('\rDownload complete                    ')

def get_song_list(url, song_filter):
    #Fetch source
    response = requests.get(url)
    data = response.text
    data = data.split('\n')
    #temp
    # with open('cache', 'r', encoding='iso-8859-1') as f:
        # data = f.readlines()
    #filter out all lines with links in them
    links = [ x for x in data if 'href' in x and song_filter in x ]
    #Replace the . in filter for regex safe \.
    regex = re.compile(r"a href=\"(.*%s)\"" % "\.".join(song_filter.split(".")))
    all_filtered_links = []
    for link in links:
        match = regex.search(link)
        all_filtered_links.append(match.group(1))
    #There might be doubles, that only have a different affix (<song>_efbd9.latin.abc)
    only_uniques = {}
    for link in all_filtered_links:
        split_on_filename = link.split(".")
        split_on_underscore = split_on_filename[0].split("_")
        #some filenames are just gibbereish, they dont split on _
        if len(split_on_underscore) == 1:
            only_uniques[split_on_filename[0]] = "%s/%s" % (url, link)
            continue
        #everything besides the unique identifier
        song_name = '_'.join(split_on_underscore[:-1])
        #The list is ordered, so we just replace it if its
        #already there
        only_uniques[song_name] = "%s/%s" % (url, link)
    #All done!
    return only_uniques.values()

if __name__ == '__main__':
    main()
