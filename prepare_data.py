import pandas as pd

import math
import statistics

from collections import Counter

from functions import getTokenCountAsData, getTokenList

articleData = pd.read_csv('fataburen_articles_diva.csv')

articleData['Pages'] = articleData['EndPage']-articleData['StartPage']+1  # add pagecount as separate column in dataframe

articleData = articleData[articleData['NBN'].str.contains('nordiskamuseet')]  # clean data by removing duplicate articles added by other institutions

articleData['Name'] = articleData['Name'].str.replace(' (Nordiska museet [877150])', '', regex=False)
articleData['Name'] = articleData['Name'].str.replace(' (Stiftelsen Nordiska museet)', '', regex=False)


keywordsData = getTokenCountAsData(articleData, 'Keywords', 'Keywords', [])
authorsData = getTokenCountAsData(articleData, 'Name', 'Authors', [])

unique_keywords = keywordsData['Keywords'].unique()
unique_authors = authorsData['Authors'].unique()


articleData.to_csv('fataburen_articles_diva_processed.csv', columns=['Name', 'PID', 'Title', 'Keywords', 'StartPage', 'EndPage', 'Pages', 'Year', 'NBN'], index=False)

# authorData = pd.DataFrame(columns=['Name','ArticlesTotal','PagesTotal','EarliestArticle','LatestArticle','KeywordsUsed','BornYear','Gender'])

authorData = {}
keywordData = {}

for author in unique_authors:
    authorData[author] = {'Name': author, 'ArticlesTotal': 0, 'PagesTotal': 0, 'EarliestArticle': '9999', 'LatestArticle': '1', 'Articles': [], 'ArticleMean': '', 'ActiveYears': 0, 'KeywordsUsed': [], 'BornYear': '', 'Gender': ''}

for keyword in unique_keywords:
    keywordData[keyword] = {'Keyword': keyword, 'ArticlesTotal': 0, 'PagesTotal': 0, 'EarliestArticle': '9999', 'LatestArticle': '1', 'Articles': [], 'ArticleMean': '', 'ActiveYears': 0, 'AuthorsUsed': []}


for row in articleData.itertuples():
    authorList = getTokenList(row[2])
    keywordList = getTokenList(str(row[34]))
    for author in authorList:
        authorData[author]['ArticlesTotal'] = authorData[author]['ArticlesTotal'] + 1
        if not math.isnan(row[18]):  # If page count exists
            authorData[author]['PagesTotal'] = authorData[author]['PagesTotal'] + row[18]
        if int(row[16]) < int(authorData[author]['EarliestArticle']):
            authorData[author]['EarliestArticle'] = row[16]
        if int(row[16]) > int(authorData[author]['LatestArticle']):
            authorData[author]['LatestArticle'] = row[16]
        authorData[author]['Articles'].append(float(row[16]))  # add article year to list
        for keyword in keywordList:
            if not keyword == 'nan':
                authorData[author]['KeywordsUsed'].append(keyword)

    for keyword in keywordList:
        if not keyword == 'nan':
            keywordData[keyword]['ArticlesTotal'] = keywordData[keyword]['ArticlesTotal'] + 1
            if not math.isnan(row[18]):  # If page count exists
                keywordData[keyword]['PagesTotal'] = keywordData[keyword]['PagesTotal'] + row[18]
            if int(row[16]) < int(keywordData[keyword]['EarliestArticle']):
                keywordData[keyword]['EarliestArticle'] = row[16]
            if int(row[16]) > int(keywordData[keyword]['LatestArticle']):
                keywordData[keyword]['LatestArticle'] = row[16]
            keywordData[keyword]['Articles'].append(float(row[16]))  # add article year to list
            for author in authorList:
                keywordData[keyword]['AuthorsUsed'].append(author)

authorDataAsList = []

for item in authorData.items():
    item[1]['ActiveYears'] = int(item[1]['LatestArticle']) - int(item[1]['EarliestArticle']) + 1
    item[1]['EarliestArticle'] = str(item[1]['EarliestArticle'])+'-01-01'
    item[1]['LatestArticle'] = str(item[1]['LatestArticle'])+'-12-01'
    keywordsUsed = Counter(item[1]['KeywordsUsed']).most_common()
    item[1]['KeywordsUsed'] = keywordsUsed
    item[1]['ArticleMean'] = statistics.mean(item[1]['Articles'])

    authorDataAsList.append(item[1])

authorDataPanda = pd.DataFrame(authorDataAsList)

print(authorDataPanda.head())

keywordDataAsList = []

for item in keywordData.items():
    item[1]['ActiveYears'] = int(item[1]['LatestArticle']) - int(item[1]['EarliestArticle']) + 1
    item[1]['EarliestArticle'] = str(item[1]['EarliestArticle'])+'-01-01'
    item[1]['LatestArticle'] = str(item[1]['LatestArticle'])+'-12-01'
    authorsUsed = Counter(item[1]['AuthorsUsed']).most_common()
    item[1]['AuthorsUsed'] = authorsUsed
    item[1]['ArticleMean'] = statistics.mean(item[1]['Articles'])

    keywordDataAsList.append(item[1])

keywordDataPanda = pd.DataFrame(keywordDataAsList)

print(keywordDataPanda.head())

authorDataPanda.to_csv('fataburen_authors.csv', index=False)

keywordDataPanda.to_csv('fataburen_keywords.csv', index=False)
