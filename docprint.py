##  docprint.py
##  June 4, 2016
##  Vito D'Orazio
##  Contact: vjdorazio@gmail.com
##
## Reads filedelim.json, a json file that contains an entry for each path to a text file, its document delimiter, and the number of documents in the collection.
## Writes a JSON file
##
##
##   Redistribution and use in source and binary forms, with or without modification,
##   are permitted under the terms of the GNU General Public License:
##   http://www.opensource.org/licenses/gpl-license.html
##
## python 3.4.3

## List of subroutines: TrimString, Filter


import glob # for extracting list of files in a location
import collections # for counting duplicate lines in a document
import re # for checking if input is valid python regex
import sys # for exiting the script with sys.exit("Error message")
import os # for removing a file
from os import walk # for walking through directories and pulling all files
import json # reading and writing json
import uuid # for generating unique ids
import copy



# ======== globals =========== #

# hash used to translate dates
month_number = {'Jan':'01', 'Feb':'02', 'Mar':'03','Apr':'04', 'May':'05', 'Jun':'06','Jul':'07', 'Aug':'08', 'Sep':'09','Oct':'10', 'Nov':'11', 'Dec':'12'}

storyN=0; # document count
kfile=0; # number of input files processed
body=""; # text between a DOCS and LANGUAGE tags
filestuff = ""; # name of file read from filedelim.json
filename = "";
mydump = {}
lnregex = "\s*\d+ of \d+ DOCUMENTS\s*"

# ======== subroutines =========== #

def Filter (myfout, mybody, myfilename, mytout, mn):
    #takes a body between a DOC and language tags
    #prints relevant news into output files
    
    # used for indexing purposes
    firsttext = 0
    gotHL=0
    ktext = 0
    fh = myfout
    fh2 = mytout
    
    # text of news story
    text = "" # the body of the news story
    
    # output per news story
    headline = "Headline Not Found"
    dateline = "Dateline Not Found"
    source = "Source Not Found"
    byline = "Byline Not Found"
    section = "Section Not Found"
    storylength = "Length Not Found"
    language = "Language Not Found"
    subject = "Subject not found"
    org = "Organization not found"
    geog = "Geographic not found"
    loaddate = "Load-date not found"
    pubtype = "Publication-type not found"
    key = "" # every story gets assigned a key after MATCH finishes
    date = ""
    collection = myfilename;
    
    values = mybody.split('\n')
    for ka in range(len(values)):
        val = values[ka]
        val=val.strip()
    
        # Skipping blank lines
        if not val:
            continue
    
        # Check to see if we have a "GEOGRAPHIC"
        myregex = re.compile("GEOGRAPHIC:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            geog = re.sub('GEOGRAPHIC: ', '', val)
            continue
        
        # Check to see if we have a "LOAD-DATE"
        myregex = re.compile("LOAD-DATE:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            loaddate = re.sub('LOAD-DATE: ', '', val)
            continue
        
        # Check to see if we have a "PUBLICATION-TYPE"
        myregex = re.compile("PUBLICATION-TYPE:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            pubtype = re.sub('PUBLICATION-TYPE: ', '', val)
            continue
        
        # Check to see if we have a "ORGANIZATION"
        myregex = re.compile("ORGANIZATION:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            org = re.sub('ORGANIZATION: ', '', val)
            continue
        
        # Check to see if we have a "SUBJECT"
        myregex = re.compile("SUBJECT:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            subject = re.sub('SUBJECT: ', '', val)
            continue


        # Check to see if we have a "LANGUAGE"
        myregex = re.compile("LANGUAGE:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            language = re.sub('LANGUAGE: ', '', val)
            continue
    
    
        # Check to see if we have a "BYLINE"
        myregex = re.compile("BYLINE:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            byline = re.sub('BYLINE: ', '', val)
            continue
    
        # Check to see if we have a "SECTION"
        myregex = re.compile("SECTION:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            section = re.sub('SECTION: ', '', val)
            continue

        # Check to see if we have a "LENGTH"
        myregex = re.compile("LENGTH:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            storylength = re.sub('LENGTH: ', '', val)
            continue
        
        # Checking to see if we have a "DATELINE"
        myregex = re.compile("DATELINE:")
        mymatch = myregex.match(val)
        if(mymatch != None):
            dateline = re.sub('DATELINE: ', '', val)
            continue

        # The FIRST LINE OF TEXT is NEWS SOURCE
        myregex = re.compile("\w+")
        mymatch = myregex.match(val)
        if(mymatch != None):
            if(firsttext==0):
                firsttext=1
                source=val
                continue

        ## Avoiding "Edition" bugs for indexing the headline
        myregex = re.compile("\w+ Edition")
        mymatch = myregex.match(val)
        if(mymatch != None):
            if(ka<10):
                gotHL = ka+2; # index of the headline
                continue

        ## HEADLINE is always 2 lines after DATE, that means one line blank in the middle
        ## $gotHL is activated only after we retrieved the FIRST date
        if(gotHL==ka):
            if(headline == "Headline Not Found"):
                headline = ""
            headline = headline+val+" "
            gotHL = ka+1; # index of the line after the first line of headline
            continue

        ## Checking if the current line matches the DATE format
        myregex = re.compile("(\w+) (\d+), (\d\d\d\d)")
        mymatch = myregex.match(val)
        if(mymatch != None):
            if date=="":
                mmonth=str(mymatch.group(1))
                mday = str(mymatch.group(2))
                myear = str(mymatch.group(3))
                mmonth=mmonth[:3]
                if mmonth in mn:
                    monthno = mn[mmonth]; # convert month to numeric
                    dayno = "";
                    if (len(mday) == 2):
                        dayno = mday
                    else:
                        dayno = '0'+mday
                    newdate = myear+str(monthno)+dayno
                    date=newdate
                    gotHL = ka+2 # the index of the headline
                    continue

        ## Establishing the body of the text.
        ## The program rid.pl has been incorporated here.
        text = text+val+"\n"
        text.lstrip() #remove leading whites
        #     text =~ tr/\x00-\x08//d;  #remove between 0-8 inclusive
        #text =~ tr/\x0B-\x1F//d;   #remove between 11-31
        #text =~ tr/\x80-\xFF//d;   #remove above 128-255
  
    # Assign the story a key
    key = str(uuid.uuid4());
    t = {'collection':collection, 'headline':headline, 'date':date, 'source':source, 'dateline':dateline, 'byline':byline, 'text':text, 'language':language, 'subject':subject, 'organization':org, 'geographic':geog, 'loaddate':loaddate, 'pubtype':pubtype}
    out = {key:t}
    fh2.write(headline+"\t"+key+"\t"+collection+"\t"+date+"\t"+source+"\t"+dateline+"\t"+byline+"\t"+language+"\t"+subject+"\t"+org+"\t"+geog+"\t"+loaddate+"\t"+pubtype+"\n")
    return(out)


#####################################
# ======== main program =========== #
#####################################

outformat=input("\nWould you like to output json or MID format? Please enter \'json\' or \'MID\': ")
if(outformat!="json" and outformat != "MID"):
    print ("Not a valid entry. Exiting")
    sys.exit()

# open files #
with open("filedelim.json") as json_file:
    json_data = json.load(json_file)
if(outformat=="json"):
    fout = open("documents.json", "w")
else:
    fout = open("documents.txt", "w")
tout = open("summary.tsv","w")

# Read through the files (INFILE) in the file list (FDIR) 
for entry in json_data:
    kfile = kfile+1
    filename = entry[0]
    docdelim = entry[1]
    numdocs = entry[2]
    
    if(docdelim=="LN" or docdelim=="LexisNexis"):
        docdelim=lnregex

    myregex = re.compile(docdelim)
   
    infile = open(filename, mode="r", encoding="latin-1")
    line = infile.readline();
 
    ke = 0;
    
    while True:
        line=infile.readline()
        if not line: break
        body=""
        line=line.lstrip(); #remove leading whites
        result = myregex.match(line)
        if(result != None): #found a doc tag, extract body
            while True:
                line=infile.readline()
                if not line: break
                result = myregex.match(line)
                if(result != None):
                    infile.seek(lastline)
                    break
                body=body+line
                lastline=infile.tell()
        
            storyN = storyN+1
            t = Filter(fout, body, filename, tout, month_number)
            # print ("Story " + str(storyN))
    
            if(outformat=="json"):
                mydump.update(t)
            else:
                mykey = t.keys()
                mykey = "".join(mykey)
                fout.write("Key: "+mykey+"\n")
                fout.write("Collection: "+t[mykey]['collection']+"\n")
                fout.write("Headline: "+t[mykey]['headline']+"\n")
                fout.write("Date: "+t[mykey]['date']+"\n")
                fout.write("Source: "+t[mykey]['source']+"\n")
                fout.write("Dateline: "+t[mykey]['dateline']+"\n")
                fout.write("Byline: "+t[mykey]['byline']+"\n")
                fout.write("Language: "+t[mykey]['language']+"\n")
                fout.write("Subject: "+t[mykey]['subject']+"\n")
                fout.write("Organization: "+t[mykey]['organization']+"\n")
                fout.write("Geographic: "+t[mykey]['geographic']+"\n")
                fout.write("Loaddate: "+t[mykey]['loaddate']+"\n")
                fout.write("Pubtype: "+t[mykey]['pubtype']+"\n\n")
                fout.write(">>>>>>>>>>>>>>>>>>>>>>\n")
                fout.write(t[mykey]['text'])
                fout.write("<<<<<<<<<<<<<<<<<<<<<<\n")
                fout.write("---------------------------------------------------------------\n\n")


if(outformat=="json"):
    json.dump(mydump,fout)

json_file.close()
fout.close()
tout.close()

print(str(kfile) + " files processed, " + str(storyN) + " stories read.")




