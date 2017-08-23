from flask import render_template, request
from ipe_app import app
from ipe_app.get_data import get_data
from ipe_app.run_model import run_model
import pandas as pd

@app.route('/')
@app.route('/index')
def index():
    game_title = request.args.get('game_title')
    appdata_df = get_data(game_title) #dataframe
    appdata = {'name':'', 'developer':'', 'score_rank':'', 'release':'', 'price':''}
    result = ""
    alldata = {0:appdata}
    
    if not appdata_df.empty and game_title:
        for i in range(len(appdata_df)):
            result = run_model(appdata_df.iloc[[i]])
            result = "$"+('%.2f' % result)
            appdata = appdata_df.iloc[i].to_dict()
            appdata['price'] = "$"+('%.2f' % appdata['price'])
            appdata['score_rank'] = ('%.0f' % appdata['score_rank']+"/100")
            appdata['result'] = result
            if appdata['release'] == '0':
                appdata['release'] = "(unknown)"
            alldata[i] = appdata
    elif game_title:
        game_title = ("Couldn't find a match for '"+str(game_title)+"'; please try a different title.")
    else:
        game_title = ""   
    return render_template('index.html', game_title=game_title, alldata=alldata)
