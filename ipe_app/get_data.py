#The model itself was created in my mvp.ipynb file and saved off to saved_model.pkl
#It expects a dataframe of stuff and spits out a result.

from sqlalchemy import create_engine #SQL
import psycopg2 #SQL
import pandas as pd #SQL, python

user = 'alan' #add your username here (same as previous postgreSQL)            
host = 'localhost'
dbname = 'steamspy'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
engine = psycopg2.connect(database = dbname, user = user)

#First, prep the data to make sure it's in a format compatible with my model.
def get_data(game_title):
    if game_title:
        game_title = game_title.replace("'","") #try to protect against SQL injection
    appdata=pd.DataFrame(columns=['index', 'appid', 'name', 'developer', 'score_rank', 'release', 'price'])
    sql_query = "SELECT * FROM indie_demo WHERE LOWER(name) like '%s' ORDER BY length(name) LIMIT 3" % (str(game_title).lower()+'%')
    appdata=pd.read_sql_query(sql_query,engine)
    appdata.drop(['index'],axis=1,inplace=True)
    #appid = appdata['appid'][0]
    #print(appdata) #dataframe
    return(appdata) #this is a thing I can (mostly) dump into my data model

if __name__ == "__main__":
    #get_data("Stardew Valley") #debug: for standalone test
    get_data("Spelunky") #debug: for standalone test
