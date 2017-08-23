#The model itself was created in my mvp.ipynb file and saved off to saved_model.pkl
#It expects a dataframe of stuff and spits out a result.
import pandas as pd
import pickle #for saving off a trained model

#Okay, now load and run the actual model.
def run_model(appdata_df):
    #print(appdata_df)
    #This needs to sync up with train_model.py
    dropnames = ['appid','name','developer','publisher','release']
    dropscale = ['postowners','newowners','saleprice','price','salerevenue']
    actual_price = appdata_df['price']
    appdata = appdata_df.drop(dropnames,axis=1)
    appdata.drop(dropscale,axis=1,inplace=True)
     
    with open('saved_rf.pkl', 'rb') as fid:
        regr_rf = pickle.load(fid)

    result = round(regr_rf.predict(appdata).tolist()[0],2)
    return result
