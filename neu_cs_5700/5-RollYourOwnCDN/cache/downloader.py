import urllib2
import sys
import os

def main():
    i = 0
    urls = open("pureUrlNoFiles.txt","rw+")
    for line in urls:
        if (i < 65):
            try:
                response = urllib2.urlopen("http://54.210.1.206:50014"+line)
            except Exception as e:
                continue
            filename = line.replace("/","_")
            filename = filename[:-1]
            fo = open(filename,"w")
            html = response.read()
            fo.write(html)
            fo.close()
            i = i + 1
        else:
            return
        


if __name__ == "__main__":
    main()
