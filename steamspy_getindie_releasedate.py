#This is a standalone version of a script to store Steamspy release dates in SQL
#Note that it relies on having run the steamspy_getindie.py script first to populate the indie_games table
#Last run took about 6305 seconds to process 8546 records.

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import requests
import re
import time
from datetime import date

start = time.mktime(time.localtime())

dbname = 'steamspy'
username = 'alan'
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

#these are copied from my browser and allow me to pull 91 days of data instead of just 21 days for anonymous users
from steamspy_cookies import my_cookies

months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
release = date.today()
saledate = date(2017,6,21)

#define a parse_data function, which takes in scraped HTML and spits out a cleaned-up dict
def parse_data(data):
    release = None
    #Looking for this pattern: Release date</strong>: Feb 26, 2016 <br>
    m = re.search("Release date</strong>\:\s([\w]+)\s(\d+),\s([\d]+)\s<br>",data) #just pull straight from HTML
    if m:
        year = int(m.group(3))
        month = months[m.group(1)]
        day = int(m.group(2))
        #print("release date:",month,day,year) #debug: reporting
        release = date(year, month, day)
        #print("release date:",release,type(release))
    return(release) #debug: type is datetime.date

#define a store_data function to store time series data in SQL
#takes in int(appid), dict(game_dict), and int(start_row)
def store_data(appid, release):
    #print(time_series) #debug: should print a reconfigured dict
    release_df = pd.DataFrame(data = {'appid':appid,'release':release},index={appid})
    #print(release_df) #debug: should print data frame
    #time_series_df = time_series_df.apply(pd.to_numeric, errors='ignore') #force stuff to be numeric
    
    #WARNING! Running this script on a non-empty DB table might break stuff. Commented out for safety.
    #release_df.to_sql('indie_releasedates', engine, if_exists='append') #WARNING! make sure you start with an empty table

#Here's the __main__ function where it actually makes the calls to parse_data and store_data.
sql_query = """                                                                       
            SELECT appid FROM indie_games;          
            """
query_results = pd.read_sql_query(sql_query,engine)
print("Finished collecting APPIDs.") #debug
progress = 0
start_row = 1 #use this to track SQL rows
#for appid in query_results['appid']:
for appid in query_results['appid']:
    url = "https://steamspy.com/app/" + str(appid)
    #print(url) #debug: make sure it's working
    r = requests.get(url,cookies=my_cookies) #pull my_cookies from steamspy_cookies file
    data = r.text 
    release = parse_data(data)
    #print(release) #debug: reporting
    store_data(appid,release)
    progress += 1
    if progress%500 == 0: #debug: change this to choose how frequently to give status updates
        print("Processed",progress,"entries so far.")
finish = time.mktime(time.localtime())
runtime = finish - start
print("Finished processing",progress,"titles in",runtime,"seconds!")