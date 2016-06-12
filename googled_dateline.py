##  googled_dateline.py
##  June 4, 2016
##  Vito D'Orazio
##  Contact: vjdorazio@gmail.com
##
## Reads in the semi-structed text in 'MID' format in 'sorted_pos.txt' file and adds two fields: GoogledDateline and AmericanDateline

import sqlite3
import re # for checking if input is valid python regex
import requests
import sys
import urllib, json

# URL for google geolocation API
url = "https://maps.googleapis.com/maps/api/geocode/json?"
apikey=raw_input("\nPlease enter your Google API key for geolocation: ")
apikey = "&key="+apikey

f = open('sorted_pos.txt', 'r')
fout = open('sorted_pos2.txt','w')

k = 0

for line in f:
    
    fout.write(line)
    
    m = re.search('(?<=Dateline: ).+', line)
    if(m != None):
        if(m.group(0)=="Dateline Not Found"):
            americadateline="AmericanDateline: False"
            googleddateline="GoogledDateline: Dateline Not found"
            print googleddateline
            fout.write(googleddateline.encode('utf-8'))
            fout.write("\n")
            fout.write(americadateline)
            fout.write('\n')
        else:
            dateline=unicode(m.group(0),errors='ignore')
            apiurl = url+'address='+dateline+apikey
            response = requests.get(apiurl)
            myr = response.json()
        
            if(myr['status']=="OK"):
                usa=1
                americadateline="AmericanDateline: False"
                formatted = myr['results'][0]['formatted_address']
                googleddateline="GoogledDateline: "+formatted
                print googleddateline
                fout.write(googleddateline.encode('utf-8'))
                fout.write("\n")
            
                m = re.search('New York, NY', formatted)
                if(m != None):
                    usa = 0
                else:
                    m = re.search('Washington, DC', formatted)
                    if(m != None):
                        usa = 0

                if(usa==1):
                    components = myr['results'][0]['address_components']
                    for i in components:
                        if (i['long_name']=="United States"):
                            americadateline="AmericanDateline: True"
                fout.write(americadateline)
                fout.write('\n')
            else:
                americadateline="AmericanDateline: False"
                googleddateline="GoogledDateline: Dateline Not found"
                print googleddateline
                fout.write(googleddateline.encode('utf-8'))
                fout.write("\n")
                fout.write(americadateline)
                fout.write('\n')


f.close()
fout.close()



