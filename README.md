# FolkRNN parser

Parses all files in a folder and tries to create a FolkRNN friendly data file

Example:
```
python FolkRNN-parser.py -f downloaded_songs -o dataset.txt --skip_chords --simplify_duplets
```
Will produce a file called dataset.txt.

Here is all the options:
```

    ####################################
    #       FolkRNN ABC parser         #
    #      Create a Folk-RNN file      #
    #   from a folder with ABC files   #
    ####################################

    usage: FolkRNN-parser.py [-h] -f FOLDER_PATH -o OUTPUT [--skip_chords]
                             [--allow_all_tokens] [--print_small_tokens_list]
                             [--simplify_duplets]

    optional arguments:
    -h, --help            show this help message and exit
    -f FOLDER_PATH, --folder_path FOLDER_PATH
                          folder with abc files
    -o OUTPUT, --output OUTPUT
                          file to save
    --skip_chords         Don't include chords in final product
    --allow_all_tokens    Allow all tokens
    --print_small_tokens_list
                          Prints the list of alowed one char tokens and then quits
    --simplify_duplets    Clear out more advanced du/tri/plets into (<d> instead
                          of (<d>:<d>:<d>

```

# FolkWiki downloader

Scraps the folkwiki.se site for songs, downloads them and puts them all in a specified folder.

Currently it only works with the following url: http://www.folkwiki.se/pub/cache
Requires Python ~3.6

Example:
```
python FolkWiki.py -u http://www.folkwiki.se/pub/cache -f latin.abc -d downloaded_songs 
```
