#Uses abc2midi to check songs for warning
import sys, os, argparse
import subprocess
from pprint import pprint

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--folder_path", help="folder with abc files", required=True)
    parser.add_argument("-o", "--output", help="file to save")
    args = parser.parse_args()
    file_list = get_all_abc_files_in_folder(args.folder_path)
    file_to_output_dict = run_all_files(file_list) 
    if args.output is None:
        for k,v in file_to_output_dict.items():
            o, e, r = v[0].decode("utf-8"), v[1], v[2]
            print(" -----  %s  ------ " % k)
            for line in o.split('\n'):
                print(line)
    else:
        with open(args.output, 'w') as f:
            for k,v in file_to_output_dict.items():
                o, e, r = v[0].decode("utf-8"), v[1], v[2]
                f.write(" -----  %s  ------ \n" % k)
                for line in o.split('\n'):
                    f.write("%s\n" % line)
    print("Done")

def run_all_files(file_list):
    file_to_output_dict = {}
    for filename in file_list:
        print("Processing %s.." % filename)
        try:
            proc = subprocess.Popen(['abc2abc', filename], stdout=subprocess.PIPE)
            outs,errs = proc.communicate()
            p_status = proc.wait()
            file_to_output_dict[filename] = (outs, errs, proc.returncode)
            proc.kill()
        except subprocess.TimeoutExpired:
            proc.kill()
            file_to_output_dict[filename] = ('COULD NOT PROCESS', None)
        
    return file_to_output_dict

def get_all_abc_files_in_folder(folder_path):
    file_list = []
    for filename in os.listdir(folder_path):
        if 'abc' in filename:
            file_list.append("%s/%s" % (folder_path, filename))
    return file_list


if __name__ == '__main__':
    main()

