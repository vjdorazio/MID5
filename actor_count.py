##  actor_count.py
##  June 4, 2016
##  Vito D'Orazio
##  Contact: vjdorazio@gmail.com
##
## Reads in the semi-structed text in 'MID' format from "sorted_pos2.txt" and adds one field: Countries
## Takes Schrodt's 'CountryInfo' file as input

import re # for checking if input is valid python regex
import sys
import operator


f = open('CountryInfo.120116.txt', 'r')
ftext = open('sorted_pos2.txt','r')
fout = open('sorted_pos3.txt','w')

# dictionary of key value paris for countries
d = dict()
ccode = ""


# function for cleaning an entry into the dictionary
def clean(str):
    str=str.replace('_',' ')
    str=re.sub(r'([^\s\w]|_)+', '', str)
    str=str.strip()
    str=str.upper()
    return str;


# read in CountryInfo file
on=0
for line in f:
    
    # skip if first non-white character is #
    m = re.match('\s*#.*',line)
    if(m != None):
        continue
    
    if(on==0):
        m = re.search('-->',line)
        if(m != None):
            on=1
        else:
            continue

    m = re.match('<CountryName>(.+)</CountryName>',line)
    if(m != None):
        ccode = m.group(1)
        ccode = clean(ccode)

    m = re.match('<Nationality>',line)
    if(m != None):
        while True:
            line=f.next()
            m = re.search('</Nationality>',line)
            if(m != None):
                break

            line = clean(line)
            if not(line in d):
                d[line] = ccode

    m = re.match('<Capital>',line)
    if(m != None):
        while True:
            line=f.next()
            m = re.search('</Capital>',line)
            if(m != None):
                break
            
            line = clean(line)
            if not(line in d):
                d[line] = ccode

    m = re.match('<MajorCities>',line)
    if(m != None):
        while True:
            line=f.next()
            m = re.search('</MajorCities>',line)
            if(m != None):
                break
            
            line = clean(line)
            if not(line in d):
                d[line] = ccode

    m = re.match('<Regions>',line)
    if(m != None):
        while True:
            line=f.next()
            m = re.search('</Regions>',line)
            if(m != None):
                break
            
            line = clean(line)
            if not(line in d):
                d[line] = ccode

    m = re.match('<GeogFeatures>',line)
    if(m != None):
        while True:
            line=f.next()
            m = re.search('</GeogFeatures>',line)
            if(m != None):
                break
            
            line = clean(line)
            if not(line in d):
                d[line] = ccode



# country count dictionary
cd = dict.fromkeys(d.values(),0)
metadata = ""
text = ""

for line in ftext:
    
    m = re.match('---------------------------------------------------------------', line)
    if(m != None):
        
        textarray = text.split()
        for idx, val in enumerate(textarray):
            if(idx < len(textarray)-3):
                i4 = textarray[idx]+" "+textarray[idx+1]+" "+textarray[idx+2]+" "+textarray[idx+3]
                t1 = i4
                i4 = clean(i4)
                if(i4 in d):
                    cd[d[i4]]=cd[d[i4]]+1
                    idx=idx+3
                    continue
            if(idx < len(textarray)-2):
                i3 = textarray[idx]+" "+textarray[idx+1]+" "+textarray[idx+2]
                t1 = i3
                i3 = clean(i3)
                if(i3 in d):
                    cd[d[i3]]=cd[d[i3]]+1
                    idx=idx+2
                    continue
            if(idx < len(textarray)-1):
                i2 = textarray[idx]+" "+textarray[idx+1]
                i2 = clean(i2)
                if(i2 in d):
                    cd[d[i2]]=cd[d[i2]]+1
                    idx=idx+1
                    continue
            i = clean(textarray[idx])
            if(i in d):
                cd[d[i]]=cd[d[i]]+1
    
        cd = {k: v for k, v in cd.iteritems() if v != 0}
        sorted_cd = sorted(cd.items(), key=operator.itemgetter(1))
        
        fout.write(metadata.rstrip())
        fout.write("\nCountries: ")
        for item in sorted_cd:
            fout.write("{0} ".format(item))
        fout.write("\n\n")
        fout.write(text)
        metadata=""
        text=""
        cd = dict.fromkeys(d.values(),0)


    m = re.match('(>>>>>>>>>>>>>>>>>>>>>>)', line)
    if(m != None):
        textON=1
        text=line
        line = ftext.next()
        text=text+line
        while textON==1:
            line=ftext.next()
            m = re.match('(<<<<<<<<<<<<<<<<<<<<<<)', line)
            if(m != None):
                textON=0
                text=text+line
                break
            else:
                text=text+line
    else:
        metadata = metadata+line

f.close()
ftext.close()
fout.close()



