#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 10:37:58 2021

@author: roji
"""
import requests
import numpy as np
import pandas as pd
import json
import re
import emoji
import nltk
import flair
nltk.download('words')
words = set(nltk.corpus.words.words())



class tweet():
    def __init__(self,ticker,BEARER_TOKEN,max_results):
        self.ticker = ticker
        self.BEARER_TOKEN = BEARER_TOKEN
        self.max_results = str(max_results)
        
    def clean_tweet(self,tweet):
        tweet = re.sub("@[A-Za-z0-9]+","",tweet) #Remove @ sign
        tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet) #Remove http links
        tweet = " ".join(tweet.split())
        tweet = ''.join(c for c in tweet if c not in emoji.UNICODE_EMOJI) #Remove Emojis
        tweet = tweet.replace("#", "").replace("_", " ") #Remove hashtag sign but keep the text
        tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) \
                         if w.lower() in words or not w.isalpha())
        return tweet
    
    def get_data(self,tweet):
        data = {'id':tweet['id'],
                'created_at':tweet['created_at'],
                'text':tweet['text']}
        return data
    
    def create_data_frame(self):
        temp = '('+str(self.ticker)+')'+'(lang:en)'
        max_results = str(self.max_results)
        endpoint = 'https://api.twitter.com/2/tweets/search/recent'
        headers = {'authorization': f'Bearer {self.BEARER_TOKEN}'}
        params = {
                    'query':temp,
                    'max_results': max_results,
                    'tweet.fields': 'created_at,lang'
                    }
        response = requests.get(endpoint,
                            params=params,
                            headers=headers)
        df = pd.DataFrame()
        for tweet in response.json()['data']:
            row = self.get_data(tweet)
            df = df.append(row,ignore_index=True)
        print(df)    
        df['text'] = df['text'].map(lambda x : self.clean_tweet(x))
        return df
    
    def adding_prob_and_sentiment(self,df):
        probs = []
        sentiments = []
        sentiment_model = flair.models.TextClassifier.load('en-sentiment')
        print(df.columns)
        for tweet in df['text'].to_list():
            sentence = flair.data.Sentence(tweet)
            sentiment_model.predict(sentence)
            probs.append(sentence.labels[0].score)
            sentiments.append(sentence.labels[0].value)
        df['probs'] = probs
        df['sentiments'] = sentiments
        
        return df
    def change_sign_to_numeric(self,item):
        if item == 'POSITIVE':
            return 1
        else:
            return -1
    
    def average_sentiments(self,df):
        df['sentiments'] = df['sentiments'].map(lambda x : self.change_sign_to_numeric(x))
        df['multiply'] = df['sentiments']*df['probs']
        return df['multiply'].mean()
    
 
        
        