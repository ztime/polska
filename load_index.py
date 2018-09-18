import sys
import re

def main():
    with open('index.utf8.html', 'r') as f:
        lines = f.readlines()
        filtered_lines = []
        for line in lines:
            if '.abc' in line:
                filtered_lines.append(line)
                
        p = re.compile(r'<a href=\"(?P<filename>.+)\">(?P<name>.*)<\/a>')
        for f_line in filtered_lines:
            m = p.search(f_line)
            # print("%s %s" % (m.group('filename'), m.group('name')))
            print("%s" % (m.group('filename')))


if __name__ == '__main__':
    main()
