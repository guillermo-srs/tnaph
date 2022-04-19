import os
import sys
import tnaph as tn


if __name__ == '__main__':
    ln = len(sys.argv)
    if ln != 4:
        print("Format: read_tnaph.py <directory> <language> <termination (e.g. .py)>")
        raise TypeError("Three arguments were expected, but it received "
                        + str(ln - 1))

    directory, language, termination = sys.argv[1:]
    TN = tn.tnaph(f='./data.csv')
    for filename in os.listdir(directory):
        if filename.endswith(termination):
            name = filename.split('-')[0]
            tn.parse_file(TN, name, directory+'/'+filename, directory+'/'+name+'.tex', language=language)
    TN.save()
