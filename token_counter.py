# Counts the number of unique tokens and their occurances 
import sys

if len(sys.argv) != 2:
    print("Supply filename to script!")
    quit()

f = open(sys.argv[1], 'r').read().replace('\n', ' ')
count_tokens = {}
for token in f.split():
    if token not in count_tokens:
        count_tokens[token] = 0
    count_tokens[token] += 1

print("Token -> occurances in %s:" % sys.argv[1])
sorted_list = list(count_tokens.keys())
for k in sorted(sorted_list):
    print("%s -> %d" % (k, count_tokens[k]))

print()
print("Total number of tokens: %d" % len(count_tokens))
