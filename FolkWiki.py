import sys, os, re, argparse, requests

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
    parser.add_argument("-u", "--url", help="the url with listing of all songs", required=True)
    parser.add_argument("-f", "--filter", help="must be in the filename of the song", required=True)
    parser.add_argument("-d","--download_path", help="folder to download songs to", required=True)
    parser.add_argument("-o", "--output", help="file to save csv to", required=True)
    args = parser.parse_args()
    #get all songs
    songs_to_download = get_song_list(args.url, args.filter)
    print("Found %d songs at %s" % (len(songs_to_download), args.url))
    print("Starting download to: %s" % args.download_path)

def get_song_list(url, song_filter):
    #Fetch source
    # response = requests.get(url)
    # data = response.text
    # data = data.split('\n')
    #temp
    with open('cache', 'r', encoding='iso-8859-1') as f:
        data = f.readlines()
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
