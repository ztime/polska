#Folkwiki scraper

Scraps the folkwiki.se site for songs, downloads them and puts them all in a csv file.

Currently it only works with the following url: http://www.folkwiki.se/pub/cache
Requires Python ~3.6

Example:
```
python FolkWiki.py -u http://www.folkwiki.se/pub/cache -f latin.abc -d downloaded_songs -o all_songs.csv
```
