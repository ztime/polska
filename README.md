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

# Notes
z = rest follow by a number for length (should be 1-4 or maybe fractions aswell?)
other notes can be [A-Ga-g][,'][',] (so any combination of letter for note and , ' in any order)
accidentals = [^,=_] before a note (includes double ^^ and __ )
longer notes = <Note followed by>[2|3|4|6|7|8|9][11|12|14|15] #12 seems to be the only one present, and 11 for some reason
shorter = <note followed by>[/2|3/2|/4] (or any fraction?)
also shorthands A/ = A/2 and A// = A/4
seems that lengts can be any sort of fraction 1/2 appears alot, wouldnt that be /2? also stuff appear like a7/ is that a7/2?? 
repeat is done with |: <body> |1 <first> :|2 <second> |]
this can of course be written as <body> |[1 <first> :|[2 <second> |]
Slurs we just ignore () around stuff
duplets work well as is ([2-9]?:\d:\d -> ([2-9] (see abc notation for details, we can remove a few of them)
chords have [ and ] around them but can also have " and " around them for "normal" (Cmaj etc ) chords
for bars we just do the | simple one, skip the fat ones 
so "]|", "||", "[|" we treat as |
also :: with be treated as ":|" + "|:" (which can ofcourse be written as :: :|: :||: ALL OF WHICH IS IN THE DATA)
save newline as a symbol to train on aswell

