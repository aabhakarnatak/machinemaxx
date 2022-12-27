import urllib.request,sys,time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from pymongo import MongoClient
import csv
import json


class newScraping:
    def __init__(self):
        self.filename="NEWS.csv"

    def get_urls(self):
        pagesToGet= 1

        upperframe=[]  
        for page in range(1,pagesToGet+1):
            print('processing page :', page)
            url = 'https://www.politifact.com/factchecks/list/?page='+str(page)
            print(url)
            
            #an exception might be thrown, so the code should be in a try-except block
            try:
                #use the browser to get the url. This is suspicious command that might blow up.
                page=requests.get(url)                             # this might throw an exception if something goes wrong.
            
            except Exception as e:                                   # this describes what to do if an exception is thrown
                error_type, error_obj, error_info = sys.exc_info()      # get the exception information
                print ('ERROR FOR LINK:',url)                          #print the link that cause the problem
                print (error_type, 'Line:', error_info.tb_lineno)     #print error info and line that threw the exception
                continue                                              #ignore this page. Abandon this and go back.
            time.sleep(2)   
            soup=BeautifulSoup(page.text,'html.parser')
            frame=[]
            links=soup.find_all('li',attrs={'class':'o-listicle__item'})
            print(len(links))
            f=open(self.filename,"w", encoding = 'utf-8')
            headers="Statement,Link,Date, Source, Label\n"
            f.write(headers)
            
            for j in links:
                Statement = j.find("div",attrs={'class':'m-statement__quote'}).text.strip()
                Link = "https://www.politifact.com"
                Link += j.find("div",attrs={'class':'m-statement__quote'}).find('a')['href'].strip()
                Date = j.find('div',attrs={'class':'m-statement__body'}).find('footer').text[-14:-1].strip()
                Source = j.find('div', attrs={'class':'m-statement__meta'}).find('a').text.strip()
                Label = j.find('div', attrs ={'class':'m-statement__content'}).find('img',attrs={'class':'c-image__original'}).get('alt').strip()
                frame.append((Statement,Link,Date,Source,Label))
                f.write(Statement.replace(",","^")+","+Link+","+Date.replace(",","^")+","+Source.replace(",","^")+","+Label.replace(",","^")+"\n")
            upperframe.extend(frame)
        f.close()
        data=pd.DataFrame(upperframe, columns=['Statement','Link','Date','Source','Label'])
        data.head()

    def load_to_db(self):
        csvfile = open(self.filename, 'r',encoding='utf-8')
        reader = csv.DictReader( csvfile )
        mongo_client = MongoClient("mongodb://localhost:27017/")
        db=mongo_client.news_scraping
        db.news_urls.drop()
        header= ['Statement','Link','Date',' Source',' Label']
        
        for each in reader:
            row={}
            for field in header:
                row[field]=each[field]
        
            db.news_urls.insert_one(row)

a=newScraping()
a.get_urls()
a.load_to_db()