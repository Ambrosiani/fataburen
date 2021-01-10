import pandas as pd

import json

import dash 
import dash_core_components as dcc     
import dash_html_components as html 
from dash.dependencies import Input, Output

import plotly.express as px

from functions import filterByTokens, getUniqueValues

# load article csv into panda

articleData = pd.read_csv('fataburen_articles_diva.csv')

articleData['Pages'] = articleData['EndPage']-articleData['StartPage']+1 # add pagecount as separate column in dataframe

articleData = articleData[articleData['NBN'].str.contains('nordiskamuseet')] # clean data by removing duplicate articles added by other institutions

unique_keywords = getUniqueValues(articleData,'Keywords','Keywords',[])

unique_authors = getUniqueValues(articleData,'Name','Authors',[])


# Initiate & configure Dash to display the graphs

app = dash.Dash(__name__) 

server = app.server
  
app.layout = html.Div(children =[ 
    html.H1("Fataburen Articles 1886–2017"), 
    dcc.Dropdown(
        id='keyword',
        options=[{'label': i, 'value': i} for i in unique_keywords],
        value='Keywords',
        multi=True,
        placeholder='Select keywords (OR)'
    ),
    dcc.Dropdown(
        id='author',
        options=[{'label': i, 'value': i} for i in unique_authors],
        value='Name',
        multi=True,
        placeholder='Select authors (OR)'
    ),
    dcc.Graph(
        id = 'articlesByYearFigure'
    ),
    html.Div([
        html.H2(
            children='Selected Article: '
        ),
        html.P([
            html.Span(
                id='articleInfo',
                children=''
                ),
            html.Br(),
            'Link: ',
            html.A(
                id='outbound-link',
                href='',
                target='_blank',
                children='',
                title='')
        ])], className='one column')
])

@app.callback(
    Output('outbound-link', 'children'),
    Output('outbound-link', 'href'),
    Output('outbound-link', 'title'),
    Output('articleInfo', 'children'),
    Input('articlesByYearFigure', 'clickData'))
def display_click_data(clickData):
    print(clickData)
    if clickData != None:
        print ('Selected article: '+str(clickData['points'][0]['customdata'][0])+' ('+str(clickData['points'][0]['customdata'][1])+')')
        return clickData['points'][0]['customdata'][1], 'https://urn.kb.se/resolve?urn='+ str(clickData['points'][0]['customdata'][1]),clickData['points'][0]['customdata'][0],['Title: ', html.B(children=clickData['points'][0]['customdata'][0]), html.Br(), 'Year: ', html.B(children=clickData['points'][0]['x']), html.Br(), 'Pages: ', html.B(children=clickData['points'][0]['y']), html.Br(), 'Authors: ', html.B(children=clickData['points'][0]['customdata'][3]), html.Br(), 'Keywords:', html.B(children=clickData['points'][0]['customdata'][2])]
    else:
        return '','','',''

@app.callback(
    dash.dependencies.Output('articlesByYearFigure', 'figure'),
    dash.dependencies.Input('keyword', 'value'),
    dash.dependencies.Input('author', 'value'))
def update_graph(selected_keywords, selected_authors):
    if selected_keywords == 'Keywords' or selected_keywords == None or selected_keywords == []: # all these are versions of "Select all"
        print('Selected keywords: None')
        filteredArticleData = articleData
    else:
        print('Selected keywords:',selected_keywords)
        filteredArticleData = filterByTokens(articleData,selected_keywords,'Keywords')

    if selected_authors == 'Name' or selected_authors == None or selected_authors == []: # all these are versions of "Select all"
        print('Selected authors: None')
    else:
        print('Selected authors:',selected_authors)
        filteredArticleData = filterByTokens(filteredArticleData,selected_authors,'Name')
    
    fig = px.bar(filteredArticleData, x='Year', y='Pages', hover_data=['Title','NBN','Keywords','Name'], barmode = 'stack')
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == '__main__': 
    app.run_server(debug=False) 

