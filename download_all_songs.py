import sys
import re
import urllib.request

def main():
    BASE_URL = 'http://www.folkwiki.se/pub/cache/'
    SONGS_DIR = 'downloaded_songs'
    print ("Getting files from folkwiki")
    count = 1
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
        for line in lines:
            print('\rDownloading song %d/%d ...' % (count, len(lines)), end="")
            line = line.strip()
            file_url = "%s%s" % (BASE_URL, line)
            file_path = "%s/%s" % (SONGS_DIR, line)
            urllib.request.urlretrieve(file_url, "%s/%s" % (SONGS_DIR, line.strip()))
            count += 1
    print("\nDone")

if __name__ == '__main__':
    main()
