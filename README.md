# FolkRNN parser

Parses all files in a folder and tries to create a FolkRNN friendly data file

Example:
```
python FolkRNN-parser.py -f downloaded_songs -s folk-rnn -o dataset.txt --skip_chords
```

# FolkWiki downloader

Scraps the folkwiki.se site for songs, downloads them and puts them all in a specified folder.

Currently it only works with the following url: http://www.folkwiki.se/pub/cache
Requires Python ~3.6

Example:
```
python FolkWiki.py -u http://www.folkwiki.se/pub/cache -f latin.abc -d downloaded_songs 
```
