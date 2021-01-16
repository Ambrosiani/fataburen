import pandas as pd

import csv
import math
import statistics

from collections import Counter

from functions import filterByTokens, getTokenCountAsData, getTokenList

articleData = pd.read_csv('fataburen_articles_diva.csv')

articleData['Pages'] = articleData['EndPage']-articleData['StartPage']+1 # add pagecount as separate column in dataframe

articleData = articleData[articleData['NBN'].str.contains('nordiskamuseet')] # clean data by removing duplicate articles added by other institutions

keywordsData = getTokenCountAsData(articleData,'Keywords','Keywords',[])
authorsData = getTokenCountAsData(articleData,'Name','Authors',[])

unique_keywords = keywordsData['Keywords'].unique()
unique_authors = authorsData['Authors'].unique()


articleData.to_csv('fataburen_articles_diva_processed.csv',columns=['Name','Title','Keywords','StartPage','EndPage','Pages','Year','NBN'],index=False)

# authorData = pd.DataFrame(columns=['Name','ArticlesTotal','PagesTotal','EarliestArticle','LatestArticle','KeywordsUsed','BornYear','Gender'])

authorData = {}
keywordData = pd.DataFrame()

for author in unique_authors:
    authorData[author] = {'Name':author,'ArticlesTotal':0,'PagesTotal':0,'EarliestArticle':'9999','LatestArticle':'1','Articles':[],'ArticleMean':'','ActiveYears':0,'KeywordsUsed':[],'BornYear':'','Gender':''}

for row in articleData.itertuples():
    authorList = getTokenList(row[2])
    keywordList = getTokenList(str(row[34]))
    for author in authorList:
        authorData[author]['ArticlesTotal'] = authorData[author]['ArticlesTotal'] +1
        if not math.isnan(row[18]): #If page count exists
            authorData[author]['PagesTotal'] = authorData[author]['PagesTotal'] +row[18]
        if int(row[16]) < int(authorData[author]['EarliestArticle']):
            authorData[author]['EarliestArticle'] = row[16]
        if int(row[16]) > int(authorData[author]['LatestArticle']):
            authorData[author]['LatestArticle'] = row[16]
        authorData[author]['Articles'].append(float(row[16])) # add article year to list
        for keyword in keywordList:
            if not keyword == 'nan':
                authorData[author]['KeywordsUsed'].append(keyword)

authorDataAsList = []

for item in authorData.items():
    item[1]['ActiveYears'] = int(item[1]['LatestArticle']) - int(item[1]['EarliestArticle']) + 1
    item[1]['EarliestArticle'] = str(item[1]['EarliestArticle'])+'-01-01'
    item[1]['LatestArticle'] = str(item[1]['LatestArticle'])+'-12-01'
    keywordsUsed=Counter(item[1]['KeywordsUsed']).most_common()
    item[1]['KeywordsUsed'] = keywordsUsed
    item[1]['ArticleMean'] = statistics.mean(item[1]['Articles'])

    authorDataAsList.append(item[1])

authorDataPanda = pd.DataFrame(authorDataAsList)

print(authorDataPanda.head())

authorDataPanda.to_csv('fataburen_authors.csv',index=False)