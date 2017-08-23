#This is a standalone version of a script to store Steamspy time series data in SQL
#Note that it relies on having run the steamspy_getindie.py script first to populate the all_games table
#Last run took about 8590 seconds to process 8546 records.

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import time

start = time.mktime(time.localtime())

dbname = 'steamspy'
username = 'alan'
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

#these are copied from my browser and allow me to pull 91 days of data instead of just 21 days for anonymous users
from steamspy_cookies import my_cookies

#define a parse_data function, which takes in scraped HTML and spits out a cleaned-up dict
def parse_data(data):
    soup = BeautifulSoup(data,"lxml")
    my_data = [] 
    #I grabbed these ahead of time and 'cached' them because they're unlikely to change
    my_keys = ['Owners', 'Price', 'Players in two weeks', 'Average time per player', 'Median time per player', 'Players total', 'Average time per player', 'Median time per player', 'PCCU', 'HCCU', 'Views in the last week', 'Videos this day']
    my_values = []

    for script in soup.find_all('script'): #data I want is in <script/> blocks
        m = re.search("\[\d+.+\]",script.text) #grab big chunks, start/end with [], contain multiple time points
        if m:
            my_data.append(script.text.replace("\n"," ").replace("\r","").replace(" ","").lstrip()) #get rid of whitespace
    for chunk in my_data:
        n = re.findall('"values":\[\[([^{}]+)\]',chunk) #within the big [] chunks, split based on {...}
        if n:
            for found_values in n:
                my_values.append(list(found_values.replace(" ","").split('],['))) #break into list of individual records
    
    clean_data = {}
    for key_num in range(len(my_keys)):
        clean_data[my_keys[key_num]] = {}
        for val_chunk in my_values[key_num]: #val_chunk is a str
            values = val_chunk.split(',') #make it a list
            #make a dict, keyed on <unix epoch seconds> with value <my_keys[key_num]>, and clean it up a bit
            clean_data[my_keys[key_num]][values[0]] = values[1].replace("]","") 
    
    del clean_data['Videos this day'] #uses a different timestamp system, so toss it
    return(clean_data) #debug: type is dict

#define a store_data function to store time series data in SQL
#takes in int(appid), dict(game_dict), and int(start_row)
def store_data(appid, game_dict, start_row):
    time_series = {}
    for attrib in game_dict.keys():
        new_index = start_row #start new_index again for each attrib
        for u_time in game_dict[attrib].keys():
            if new_index not in time_series:
                time_series[new_index] = {}
            time_series[new_index]['appid'] = appid
            time_series[new_index]['seconds'] = (u_time)
            new_value = game_dict[attrib][u_time]
            time_series[new_index][attrib] = new_value
            new_index += 1
    
    #print(time_series) #debug: should print a reconfigured dict
    time_series_df = pd.DataFrame.from_dict(time_series,orient = 'index')
    #print(time_series_df) #debug: should print data frame
    time_series_df = time_series_df.apply(pd.to_numeric, errors='ignore') #force stuff to be numeric
    
    #WARNING! Running this script on a non-empty DB table might break stuff! Commented out for safety.
    #time_series_df.to_sql('indie_timeseries', engine, if_exists='append') #WARNING! make sure you start with an empty table

#Here's the __main__ function where it actually makes the calls to parse_data and store_data.
sql_query = """                                                                       
            SELECT appid FROM indie_games;          
            """
query_results = pd.read_sql_query(sql_query,engine)
print("Finished collecting APPIDs.") #debug
progress = 0
start_row = 1 #use this to track SQL rows
for appid in query_results['appid']:
    url = "https://steamspy.com/app/" + str(appid)
    #print(url) #debug: make sure it's working
    r = requests.get(url,cookies=my_cookies) #pull my_cookies from steamspy_cookies file
    data = r.text 
    store_data(int(appid),parse_data(data),start_row) #gets back a dict, immediately put it into SQL
    start_row += 91 #hardcoded because Steamspy gives us 91 time points
    progress += 1
    if progress%500 == 0: #debug: change this to choose how frequently to give status updates
        print("Processed",progress,"entries so far.")

finish = time.mktime(time.localtime())
runtime = finish - start
print("Finished processing",progress,"titles in",runtime,"seconds!")
