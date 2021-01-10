from collections import Counter
import pandas as pd
import plotly.express as px

def createTokenCount(wordList, stopWordList):
    wordCount=Counter(wordList).most_common()
    wordCountWithoutStopListWords=[]
    for tuplet in wordCount:
        if not tuplet[0] in stopWordList:
            wordCountWithoutStopListWords.append(tuplet)
    return wordCountWithoutStopListWords


def getUniqueValues(dataframe,column,columnName,stopWordList):
    tokenList = []

    for tokens in dataframe[column].str.split(';').tolist():
        if type(tokens) is list: # if entry has multiple tokens
            for token in tokens:
                tokenList.append(token)
        if type(tokens) is str: # if entry has just one token
            tokenList.append(tokens)

    tokenCount = pd.DataFrame(createTokenCount(tokenList, stopWordList))
    tokenCount.columns = [columnName, 'Count']
    unique_tokens = tokenCount[columnName].unique()
    return unique_tokens

def filterByTokens(dataframe,tokens,column):
    filters = []
    for token in tokens:
        filtered = dataframe[dataframe[column].str.contains(token, na=False, regex=False)]
        filters.append(filtered) # each token filter is added in a list
        filteredArticleData = pd.concat(filters)
    return filteredArticleData

def filterAuthors(dataframe,authors):
    fig = px.bar(dataframe, x='Year', y='Pages', hover_data=['Title','NBN'], barmode = 'stack')
    return fig