##  MIDtoDB.py
##  June 4, 2016
##  Vito D'Orazio
##  Contact: vjdorazio@gmail.com
##
## Reads in the semi-structed text in 'MID' format and writes it to a database.
## Assumes a sqlite3 database called 'middb' exists

import sqlite3
import re # for checking if input is valid python regex
import requests
import pandas.io.sql as pd # to export tab-delimited


conn = sqlite3.connect("./middb.sqlite")
c = conn.cursor()

c.execute('drop table if exists mid;')
c.execute('create table mid (Headline string,Key string,Date string,Source string,Dateline string,Byline string,Collection string,Language string,Subject string,Organization string,Geographic string,Loaddate string,Pubtype string,StoryText string,GoogledDateline string,AmericanDateline boolean,Countries string);')

textON = 0

# text of news story
text = "" # the body of the news story
    
# output per news story
headline = "Headline Not Found"
dateline = "Dateline Not Found"
source = "Source Not Found"
byline = "Byline Not Found"
key = "Key Not Found"
date = "Date Not Found"
googleddateline = "Dateline Not Found"
americandateline = False
countries = "Countries Not Found"
collection = "Collection Not Found"
language = "Language Not Found"
subject = "Subject Not Found"
organization = "Organization Not Found"
geographic = "Geographic Not Found"
loaddate = "Loaddate Not Found"
pubtype = "Pubtype Not Found"


f = open('sorted_pos3.txt', 'r')
for line in f:
    
    m = re.match('---------------------------------------------------------------', line)
    if(m != None):
        conn.execute("INSERT INTO mid(headline, key, date, source, dateline, byline, collection, language, subject, organization, geographic, loaddate, pubtype, storytext, googleddateline, americandateline, countries) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (headline, key, date, source, dateline, byline, collection, language, subject, organization, geographic, loaddate, pubtype, text, googleddateline, americandateline, countries))
        conn.commit()
        #print(headline)
        #print(key)
        #print(date)
        #print(source)
        #print(dateline)
        #print(byline)
        #print(text)
        #print('\n')

        continue
    
    if line.isspace():
        continue

    m = re.search('(?<=Headline: ).+', line)
    if(m != None):
        headline=unicode(m.group(0),errors='ignore')
        continue

    m = re.search('(?<=Key: ).+', line)
    if(m != None):
        key=unicode(m.group(0),errors='ignore')
        continue

    m = re.search('(?<=Date: ).+', line)
    if(m != None):
        date=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Source: ).+', line)
    if(m != None):
        source=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Dateline: ).+', line)
    if(m != None):
        dateline=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Byline: ).+', line)
    if(m != None):
        byline=unicode(m.group(0),errors='ignore')
        continue

    m = re.search('(?<=Collection: ).+', line)
    if(m != None):
        collection=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Language: ).+', line)
    if(m != None):
        language=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Subject: ).+', line)
    if(m != None):
        subject=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Organization: ).+', line)
    if(m != None):
        organization=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Geographic: ).+', line)
    if(m != None):
        geographic=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Loaddate: ).+', line)
    if(m != None):
        loaddate=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=Pubtype: ).+', line)
    if(m != None):
        pubtype=unicode(m.group(0),errors='ignore')
        continue

    m = re.search('(?<=Countries: ).+', line)
    if(m != None):
        countries=unicode(m.group(0),errors='ignore')
        continue
    
    m = re.search('(?<=GoogledDateline: ).+', line)
    if(m != None):
        googleddateline=unicode(m.group(0),errors='ignore')
        continue

    m = re.search('(?<=AmericanDateline: ).+', line)
    if(m != None):
        americandateline=unicode(m.group(0),errors='ignore')
        continue

    m = re.match('(>>>>>>>>>>>>>>>>>>>>>>)', line)
    if(m != None):
        textON=1
        line = f.next()
        text=line
        while textON==1:
            line=f.next()
            m = re.match('(<<<<<<<<<<<<<<<<<<<<<<)', line)
            if(m != None):
                textON=0
                text=unicode(text,errors='ignore')
                break
            else:
                text=text+line

f.close()


c.execute('create index x_key on mid(key);')
c.execute('create index x_storytext on mid(storytext);')
c.execute('select key, count(key) as how_many from mid group by key having count(key) > 1;')
c.execute('select count (*) from mid;')
startN = c.fetchone()[0]
c.execute('delete from mid where key not in(select  min(key) from mid group by storytext);')
c.execute('select count (*) from mid;')
finishN = c.fetchone()[0]
print "Started with",startN," and finished with ",finishN," stories."

mytab = pd.read_sql_query('SELECT headline, key, date, source, dateline, byline, collection, language, subject, organization, geographic, loaddate, pubtype, googleddateline, americandateline, countries from mid',conn)
mytab.to_csv('metadata.tsv', sep='\t')

conn.row_factory = lambda cursor, row: row[0]
c = conn.cursor()
ids = c.execute('SELECT key FROM mid').fetchall()

conn.commit()
conn.close()

f = open('sorted_pos3.txt', 'r')
fout = open('sorted_pos4.txt', 'w')

k1=0
for line in f:
    m = re.search('(?<=Key: ).+', line)
    if(m != None):
        key=unicode(m.group(0),errors='ignore')
        if(key in ids):
            fout.write(line)
            while True:
                line=f.next()
                m = re.match('---------------------------------------------------------------', line)
                if(m != None):
                    fout.write(line)
                    k1 = k1+1
                    break
                else:
                    fout.write(line)
print "Printed ",k1," stories to file."
f.close()
fout.close()

