from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import gmtime, strftime
import urllib.request, json
import time
from twilio.rest import Client
from flask import Flask, request, redirect

# Your Account Sid and Auth Token from twilio.com/console
account_sid = '*****'
auth_token = '**********'
client = Client(account_sid, auth_token)

#Set up Environent
hour = int(strftime("%H", gmtime())) - 1
alerted = False
numtimes = 0
cheap = []
cheap5 = []
avg = []
avg5 = []
times = []
numbers = ['*******'] #Numbers to Text

while True:
    
    print(numtimes)
    numtimes +=1 
    
    #URL's for data 
    url = "https://api.tickpick.com/1.0/listings/internal/event/3416011?mid=3416011"
    data = requests.get("https://api.tickpick.com/1.0/listings/internal/event/3416011?mid=3416011")
    
    #Grab Data
    with urllib.request.urlopen(url) as url2:
        data = json.loads(url2.read().decode())
        
    hour2 = int(strftime("%H", gmtime()))
    
    #Switch to pandas df for saving
    df = pd.DataFrame(data)[['id', 'sid', 'p', 'n', 'sp']]
    df.columns = ['id', 'section', 'price', 'notes', 'num_seats']
    df = df[df.price > 1500]
    df = df.sort_values('price')
    df.head()
    
    #Looking for 5 seats together 
    df_5 = df[df['num_seats'].apply(lambda x: 5 in x)]
    
    # Add new prices to lists
    cheap.append(min(df.price))
    cheap5.append(min(df_5.price))
    avg.append(sum(df.price) / len(df.price))
    avg5.append(sum(df_5.price) / len(df_5.price))
    times.append(strftime("%m/%d %H:%M:%S", gmtime()))
    
    # create df
    df = pd.DataFrame({'time':times, 
              'cheapest':cheap,
              'cheapest_5_seats':cheap5, 
              'avg_price':avg, 
              'avg_5_seats':avg5})
    
    #Find cheapest 
    cheapest = list(df['cheapest'])[-1]
    cheapest_5 = list(df['cheapest_5_seats'])[-1]
    mess = "{} is currently the cheapest ticket on TicketFly. {} is the cheapest ticket with 5 together.".format(cheapest, cheapest_5)
    
    # Send Messages
    
    if (cheapest < 2700) and (alerted == False): 
        
        message = client.messages.create(
                                         body = 'ALERT: Prices dropped below $2700',
                                         from_= '+16178906174',
                                         to   = '+16177501121'
                                         )
        alerted = True
        
    
    if hour != hour2:  
        for number in numbers:

            message = client.messages.create(
                                         body = mess,
                                         from_= '+16178906174',
                                         to   = number
                                         )
        hour = int(strftime("%H", gmtime()))
        alerted = False
    
    df.to_csv('~/Projects/Super_Bowl/prices.csv')
    
    time.sleep(60*5) #Repeat every 5 minues

