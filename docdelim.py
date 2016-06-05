## docdelim.py
## June 4, 2016
## Vito D'Orazio
## vjdorazio@gmail.com
##
## Writes filedelim.json, a file that contains a list of all the text files, their delimiters, and the number of docs.
## Note that this writes the names of all files listed in the directory provided by the user.
## python 3.4.3

import glob # for extracting list of files in a location
import collections # for counting duplicate lines in a document
import re # for checking if input is valid python regex
import sys # for exiting the script with sys.exit("Error message")
import os # for removing a file
from os import walk # for walking through directories and pulling all files
import json # reading and writing json

## Functions
def autoDelimit (file):
    with open(file) as infile:
        counts = collections.Counter(l.strip() for l in infile)
    for line, count in counts.most_common():
        if(count>1):
            if(line.isspace()) or not line:
                continue
            k=input("\nFor document " + file + ", is " + line + " your delimiter? Answer y/n, or answer skip to move to the next file without locating a delimiter: ")
            if(k=="skip"):
                return([file,"No delimiter",0])
            if( k == "y") or (k == "yes"):
                return([file,line,count])
                break
            else:
                continue
        else:
            print("\n I could not find a document delimiter.")
            return([file,"No delimiter",0])

## Main
myfiles = open("filelist.json","w")
mydump = []
lnregex = "\s*\d+ of \d+ DOCUMENTS\s*"

print("\n\nWelcome to PreText.")

print("\nPlease tell me where your text files are. For example, input something like /Users/vjdorazio/documents/.")

while True:
    loc = input("\nPlease tell me the location of the text files: ")
    for (dirpath, dirnames, filenames) in walk(loc):
        for i in range(len(filenames)):
            if filenames[i].startswith('.'): #skips over hidden files
                filenames[i]=""
            filenames[i]= dirpath+"/"+filenames[i]
        mydump.extend(filenames)

    #for name in glob.glob(loc + "*"):
    #   myfiles.write(name + "\n")
    k = input('Are there more files someplace else? Answer y/n: ')
    if (k == "n") or (k == "no"):
        break

json.dump(mydump,myfiles)
myfiles.close()

with open("filelist.json") as json_file:
   json_data = json.load(json_file)

myfiledelim = open("filedelim.json", "w")

print("\nIf the files contain more than one document, you will need to enter the document delimiter. That is the line that signals we are at a new document. You may use python3 regular expressions to describe the delimiter, or just a string that delimits your documents.")
k1 = 0
mydump = []
for file in json_data:
    file = file.rstrip('\n')

    if not os.path.isfile(file):
        print(file)
        continue

    myfile = open(file, mode="r", encoding="latin-1")
    if(k1 == 1):
        delim = input("\nFor file " + file + ", please enter a python3 regular expression or just a string that delimits your documents. If you'd like me to try to find it automatically, enter \'automate\'. If you have LexisNexis documents, enter \'LN\': ")
    elif(k1 == 0):
        delim = input("\nFor file " + file + ", please enter a python3 regular expression or just a string that delimits your documents. If you'd like me to try to find it automatically, enter \'automate\'. If you have LexisNexis documents, enter \'LN\': ")
        k1 = input("\nShould I use this delimiter for every file? Answer y/n: ")
        if(k1 == "n") or (k1 == "no"):
            k1 = 1
        else:
            k1 = 2

    if(delim=="automate"):
        myfile.close()
        stuff = autoDelimit(file)
        outdelim=stuff[1]
        count=stuff[2]
    elif(delim=="LN" or delim=="LexisNexis"):
        count = 0
        myregex = re.compile(lnregex)
        for line in myfile:
            result = myregex.match(line)
            if(result != None):
                count += 1
        outdelim=delim
    else:
        count = 0
        try:
            re.compile(delim)
            is_valid = True
        except re.error:
            is_valid = False
        if(is_valid):
            myregex = re.compile(delim)
            for line in myfile:
                result = myregex.match(line)
                if(result != None):
                    count += 1
            outdelim=delim
        else:
            for line in myfile:
                line = line.rstrip('\n')
                if(delim == line):
                    count += 1
            outdelim=delim

    if(count==0):
        count=1 # if no delimiter is located, the entire file is assumed to be one document
    print("\nThe delimiter in " + file + " is " + outdelim + " and there are " + str(count) + " documents.")
    mydump.extend([[file,outdelim,str(count)]])

json.dump(mydump,myfiledelim)
#myfiledelim.write(file + "\t" + outdelim + "\t" + str(count) + "\n")


try:
    os.remove("filelist.txt")
    os.rename("filedelim.json","filelist.tsv")
except OSError:
    pass

k1=input("\nAre the above files, delimiters, and document counts correct? Answer y/n: ")
if(k1=="n") or (k1=="no"):
    try:
        os.remove("filelist.tsv")
        print("\nYou answered no, so I deleted the output file. Exiting.")
    except OSError:
        pass

myfiles.close()
myfiledelim.close()






