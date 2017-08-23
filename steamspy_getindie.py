#This is the standalone version of my Steamspy retrieval program, to get around the ipynb memory limitations.
#Takes ~32 seconds.

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import requests
import time
start = time.mktime(time.localtime())

dbname = 'steamspy'
username = 'alan'
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname)) #this should already exist

#get Indie games on Steam and stuff the data into a pandas dataframe
r = requests.get('https://steamspy.com/api.php?request=genre&genre=Indie') #API call: get 'Indie' games
indie_games = r.json()
print("Retrieving records for all Indie games:",len(indie_games)) #debug: get a count, should be around 8500

indie_games_tags = {}
for game in indie_games.keys():
    if indie_games[game]['tags'] == []:
        indie_games[game]['tags'] = {} #if this is empty, make sure it's a dict and not a list
    if indie_games[game]['price']:
        indie_games[game]['price'] = float(indie_games[game]['price'])/100 #I want price in $0.00 format
        
    #start building a tags table
    indie_games_tags[game] = {}
    indie_games_tags[game]['appid'] = indie_games[game]['appid']
    
    #expand out the 'tags' sub-dict into individual top-level dict entries
    for tag_name in indie_games[game]['tags'].keys(): #[game]['tags'] should be a Python dict of tag_name:tag_count
        tag_value = indie_games[game]['tags'][tag_name]
        indie_games_tags[game][tag_name] = tag_value #maps the old tags sub-dict into a new tags top-level dict
        
    del(indie_games[game]['tags']) #do this LAST, after building the indie_games_tags_df table
    
indie_games_df = pd.DataFrame.from_dict(indie_games,orient = 'index') #each row should be a separate game title
indie_games_tags_df = pd.DataFrame.from_dict(indie_games_tags,orient = 'index') #each row should be a separate game title

indie_games_df[['score_rank']] = indie_games_df[['score_rank']].apply(pd.to_numeric) #force score_rank to be numeric

#stuff dataframes into postgresql
indie_games_df.to_sql('indie_games', engine, if_exists='replace')
indie_games_tags_df.to_sql('indie_games_tags', engine, if_exists='replace')

finish = time.mktime(time.localtime())
runtime = finish - start
print("Finished in",runtime,"seconds!")

