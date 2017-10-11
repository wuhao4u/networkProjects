import sys
import re

def main(filename):
    # urlList = re.findall('<a href="(.+?)">',httpString)
    with open(filename) as f:
        for line in f:
            if '<a href=' in line:
                print re.findall('<a href="(.+?)">',line)[0]

if __name__ == '__main__':
    main(sys.argv[1])