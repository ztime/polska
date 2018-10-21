import sys
import os
import subprocess
import argparse
import tempfile

from pprint import pprint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-f",
            "--folder_path",
            help="Folder with abc files",
            required=True)
    parser.add_argument(
            "-o",
            "--output",
            help="File to save",
            required=True)
    args = parser.parse_args()
    #Find all files
    filenames = get_all_filenames(args.folder_path)
    total_no_files = len(filenames)
    total_err_files = 0
    c_file = 0
    dot_counter = 0
    output_file = open(args.output, 'w')
    for filename in filenames:
        c_file += 1
        print("Processing file %d/%d" % (c_file, total_no_files), end="")
        if c_file % 100 == 0:
            dot_counter += 1
            dot_counter = dot_counter % 4
        print("."*(dot_counter), end='')
        print(" "*20, end='')
        print("\r", end='')
        errors = check_file(filename)
        if errors is not None:
            total_err_files += 1
            output_file.write('-- Errors in file %s --\n' % filename)
            for err in errors:
                output_file.write('\t%s\n' % err)
    if total_err_files > 0:
        err_percent = (float(total_err_files)/float(total_no_files)) * 100.0
    else:
        err_percent = 0.0
    print(" ")
    print("Total files read %d in %s" % (total_no_files, args.folder_path))
    print("Errors found in %d of them" % total_err_files)
    print("Error percentage of %.2f%%" % err_percent)
    output_file.write("\nTotal files read %d in %s\n" % (total_no_files, args.folder_path))
    output_file.write("Errors found in %d of them\n" % total_err_files)
    output_file.write("Error percentage of %.2f%%\n" % err_percent)
    output_file.close()

def check_file(filename):
    file_contents = open(filename, 'r').readlines()
    tmp_file = None
    if ''.join(file_contents).find("X:") == -1:
        file_contents.insert(0, 'X:0\n')
        tmp_file = tempfile.NamedTemporaryFile(mode='w')
        filename = tmp_file.name
        for line in file_contents:
            tmp_file.write(line)
        tmp_file.flush()
    arguments = ['abc2midi', filename , '-c']
    p = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    try:
        lines_from_abc = stdout.decode('utf-8').split('\n')
    except UnicodeDecodeError as e:
        lines_from_abc = ['', 'Could not decode utf-8, probably invalid chars in abc file']
    if tmp_file is not None:
        tmp_file.close()
    if len(lines_from_abc) > 1 and lines_from_abc[1] != '':
        return lines_from_abc[1:]
    else:
        return None

# Scans a folder for all files with abc in it and returns a 
# list of full paths
def get_all_filenames(folder):
    file_list = []
    for filename in os.listdir(folder):
        if 'abc' in filename:
            file_list.append("%s/%s" % (folder, filename))
    return file_list

if __name__=='__main__':
    main()
