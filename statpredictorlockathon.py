# -*- coding: utf-8 -*-
"""StatPredictorLockathon.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mfAngHdV8hC_YVoJbU7jb4iL7EWXS5gJ
"""

from google.colab import files                   # since data was taken from kaggle, hence kaggle token used
import os
uploaded = files.upload()

!ls -lha kaggle.json
!pip install statsmodels==0.11.0rc1
!pip install -q kaggle
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle
!chmod 600 ~/.kaggle/kaggle.json
!kaggle datasets download --force -d sudalairajkumar/covid19-in-india

!unzip covid19-in-india.zip                            # covid19-in-india.zip has been pushed seperately in the repo

import pandas as pd
import numpy as np
import datetime
import warnings
from datetime import timedelta
warnings.filterwarnings('ignore')
raw_data = pd.read_csv('covid_19_india.csv')

x = np.array(raw_data['Time'])
u = np.unique(x)
print(u)                                                                      # replacing the AM-PM timestyle with 24 hour timestyle
raw_data['Time'][raw_data['Time'] == '10:00 AM'] = '10:00:00' 
raw_data['Time'][raw_data['Time'] == '10:00 AM'] = '10:00:00' 
raw_data['Time'][raw_data['Time'] == '8:00 AM'] = '08:00:00'
raw_data['Time'][raw_data['Time'] == '5:00 PM'] = '17:00:00'                                     # replacing the AM-PM timestyle with 24 hour timestyle
raw_data['Time'][raw_data['Time'] == '6:00 PM'] = '18:00:00'
raw_data['Time'][raw_data['Time'] == '7:30 PM'] = '19:30:00'
raw_data['Time'][raw_data['Time'] == '8:30 PM'] = '20:30:00'
raw_data['Time'][raw_data['Time'] == '9:30 PM'] = '21:30:00'     
print(raw_data['Time'])

raw_data['Date'] = raw_data['Date'] + '20'
raw_data['Datetime'] = raw_data['Date'] + ' ' + raw_data['Time']
for i in range(len(raw_data['Datetime'])):
  raw_data['Datetime'][i] = datetime.datetime.strptime(raw_data['Datetime'][i],'%d/%m/%Y %H:%M:%S')  
print(raw_data['Datetime'])                                                                              # converting all the dates in string to datetime data type

statewise = raw_data.groupby('State/UnionTerritory')['Confirmed','Deaths','Cured'].max()
statewise['Active'] = statewise['Confirmed'] - statewise['Deaths'] - statewise['Cured']
print(statewise)                                                                # displaying statewise statistics as they stand for better understanding

from statsmodels.tsa.arima_model import ARIMA
from matplotlib import pyplot as plt
from pandas.plotting import autocorrelation_plot

def predcountry(raw_data,days_in_advance):
  raw_data['Datetime'] = raw_data['Date'] + ' ' + raw_data['Time']
  for i in range(len(raw_data['Datetime'])):
    raw_data['Datetime'][i] = datetime.datetime.strptime(raw_data['Datetime'][i],'%d/%m/%Y %H:%M:%S')  
  #print(raw_data['Datetime'])     
  country_data = raw_data.groupby("Datetime")[["Confirmed","Cured","Deaths"]].sum().reset_index()
  country_data['Active'] = country_data['Confirmed'] - country_data['Cured'] - country_data['Deaths']            
  #print(country_data)                             
  country_data['ds'] = country_data['Datetime']
  country_data['y'] = country_data['Confirmed'] 
  testing = country_data.loc[:,('Confirmed','Datetime')]
  model2 = ARIMA(testing['Confirmed'],order = [5,1,0])
  model2 = model2.fit()
  forecast = model2.forecast(steps = 30)
  pred = list(forecast[0].astype(int))
  y = country_data['Confirmed']
  y = y.append(pd.Series(pred))
  y = y.reset_index(drop = True)
  #print(y)
  x = pd.Series(pd.date_range(raw_data['Date'][0],periods=len(y)))
  #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
   #print(x)
  plt.plot(x,y,linestyle = 'solid')
  plt.show()
  return pred[days_in_advance].astype(int),x,y

+mmmmmmmmmmmmmmval,x,y = predcountry(raw_data,2)
print("Expected confirmed cases by " + str((datetime.datetime.today().date()+timedelta(days=10)))+" are " + str(val))

def pred_state(raw_data,state,days_in_advance):
  delh = raw_data[raw_data['State/UnionTerritory'] == state].reset_index()
  #print(delh)
  tdata = delh.loc[:,('Datetime','Confirmed')]
  model1 = ARIMA(tdata['Confirmed'],order = [5,1,0])
  model1 = model1.fit(trend = 'c')
  forec = model1.forecast(steps = 30)
  pred = list(forec[0])
  y = delh['Confirmed']
  y = y.append(pd.Series(pred))
  y = y.reset_index(drop = True)
  #print(y)
  x = pd.Series(pd.date_range(raw_data['Date'][0],periods=len(y)))
  return pred[days_in_advance].astype(int),x,y

state = 'Delhi'
days = 5
val2,x1,y1 = pred_state(raw_data,state,days)
print("Expected Confirmed cases in " + state + " by " + str((datetime.datetime.today().date()+timedelta(days=days)))+" is "+str(val2))
plt.plot(x1,y1,linestyle = 'dashed')