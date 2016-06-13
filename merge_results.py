##  merge_results.py
##  June 13, 2016
##  Vito D'Orazio
##  Contact: vjdorazio@gmail.com
##
##  program to merge classifier output with texts
##
##  execute in unix: python merge_results.py
##  outputs sorted_pos.txt

import re # for checking if input is valid python regex
import sys
import operator


f1 = raw_input("\nPlease enter the path and filename for the predictions file: ")
f2 = raw_input("\nPlease enter the path and filename for the documents file: ")

fpred = open(f1,'r')
ftext = open(f2, 'r')
fout = open('sorted_pos.txt','w')

mykeys = dict()
for line in fpred:
    vals = line.split()
    mykeys[vals[1]]=vals[2]

k1=0
k2=0
for line in ftext:
    m = re.search('(?<=Key: ).+', line)
    if(m != None):
        key=unicode(m.group(0),errors='ignore')
        if key in mykeys:
            if(mykeys[key]=='1'):
                fout.write(line)
                while True:
                    line=ftext.next()
                    m = re.match('---------------------------------------------------------------', line)
                    if(m != None):
                        fout.write(line)
                        k1 = k1+1
                        break
                    else:
                        fout.write(line)
        else:
            print "Key ",key," not in mykeys.\n"
            k2 = k2+1
print "Printed ",k1," stories to file."
print k2," keys not recognized."

fpred.close()
ftext.close()
fout.close()