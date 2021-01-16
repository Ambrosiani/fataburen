import pandas as pd

import json

import dash 
import dash_core_components as dcc     
import dash_html_components as html 
from dash.dependencies import Input, Output

import plotly.express as px

from functions import filterByTokens, getTokenCountAsData

# load article csv into panda

articleData = pd.read_csv('fataburen_articles_diva.csv')

articleData['Pages'] = articleData['EndPage']-articleData['StartPage']+1 # add pagecount as separate column in dataframe

articleData = articleData[articleData['NBN'].str.contains('nordiskamuseet')] # clean data by removing duplicate articles added by other institutions

keywordsData = getTokenCountAsData(articleData,'Keywords','Keywords',[])
unique_keywords = keywordsData['Keywords'].unique()

#authorsData = getTokenCountAsData(articleData,'Name','Authors',[])
authorsData = pd.read_csv('fataburen_authors.csv')

authorsDataByArticleCount = authorsData.copy()
authorsDataByPageCount = authorsData.copy()
authorsDataByEarliestArticle = authorsData.copy()

authorsDataByArticleCount.sort_values(by=['ArticlesTotal','Name'], ascending=[True,False], inplace=True)
authorsDataByPageCount.sort_values(by=['PagesTotal','Name'], ascending=[True,False], inplace=True)
authorsDataByEarliestArticle.sort_values(by=['EarliestArticle','Name'], ascending=[False,False], inplace=True)
authorsDataByEarliestArticle['LatestArticleYear'] = authorsDataByEarliestArticle['LatestArticle'].str.slice(0, 4)
authorsDataByEarliestArticle['ArticleMeanRounded'] = round(authorsDataByEarliestArticle['ArticleMean'], 0)

unique_authors = authorsData['Name']

# Initiate & configure Dash to display the graphs

app = dash.Dash(__name__, suppress_callback_exceptions=True) 

server = app.server

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

app.layout = url_bar_and_content_div

# Navigation

header = html.Div(children=[
    html.H1('Fataburen Articles 1886–2017'),
    dcc.Link('Explore articles', href='/explore'),' • Article Statistics: ',
    dcc.Link('Authors by Article Count', href='/authors-articles'),' • ',
    dcc.Link('Authors by Page Count', href='/authors-pages'),' • ',
    dcc.Link('Authors by Active Period', href='/authors-period'),' • ',
    dcc.Link('Keywords by Author', href='/keywords-author'),' • ',
    dcc.Link('Keywords by Article Count', href='/keywords-articles'),' • ',
    dcc.Link('Keywords by Page Count', href='/keywords-pages'),' • ',
    dcc.Link('Keywords by Active Period', href='/keywords-period'),' • ',
    dcc.Link('About', href='/about'),
    ],
    id='header'
)

# Layouts

layout_explore = html.Div(children =[ 
    header,
    html.P(['Explore the content of Fataburen, the yearbook/journal of Nordiska museet & Skansen. Work in progress by ',
        html.A(
            children='Aron Ambrosiani',
            href='https://twitter.com/AronAmbrosiani/'
            ),
        '. Code available at ',
        html.A(
            children='github.com/ambrosiani/fataburen/',
            href='https://github.com/ambrosiani/fataburen/')
        ]), 
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
    html.P(
        id='articleCount',
        children=''),
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
            'Link to DiVA page: ',
            html.A(
                id='outbound-link',
                href='',
                target='_blank',
                children='',
                title=''),
            html.Br(),
            'Direct link to PDF: ',
            html.A(
                id='pdf-link',
                href='',
                target='_blank',
                children='',
                title='')
        ])], className='one column')
])

layout_authors_articles = html.Div(children=[
    header,
    html.Div(
        dcc.Graph(
            id='authorsByArticles',
            figure=px.bar(
                authorsDataByArticleCount, 
                x='ArticlesTotal', 
                y='Name',
                orientation='h',
                title='Authors by Article Count',
                hover_name='Name',
                hover_data={'Name':False}
            ), 
            style={'height':len(authorsDataByArticleCount)*15},
        ),
        className='fullheight'
    )
])

layout_authors_pages = html.Div(children=[
    header,
    html.Div(
        dcc.Graph(
            id='authorsByPages',
            figure=px.bar(
                authorsDataByPageCount, 
                x='PagesTotal', 
                y='Name',
                orientation='h',
                title='Authors by Page Count',
                hover_name='Name',
                hover_data={'Name':False}
            ), 
            style={'height':len(authorsDataByArticleCount)*15},
        ),
        className='fullheight'
    )
])

layout_authors_period = html.Div(children=[
    header,
    html.Div(
        ['Bars show timespan from earliest to latest published article. Mean publishing year displayed on hover.',
                dcc.Graph(
                    id='authorsByPeriod',
                    figure=px.timeline(
                        authorsDataByEarliestArticle, 
                        x_start='EarliestArticle',
                        x_end='LatestArticle',
                        y='Name',
                        title='Authors by Active Period',
                        hover_name='Name',
                        hover_data={
                            'EarliestArticle':'|%Y',
                            'LatestArticle': False,
                            'LatestArticleYear':True,
                            'ArticleMeanRounded': True,
                            'Name':False
                        }
                    ), 
                    style={'height':len(authorsDataByArticleCount)*15}
        )],
        className='fullheight'
    ) 
])

layout_keywords_author = html.Div(children=[
    header,
    html.Div('Placeholder keywords author')]
    )

layout_keywords_articles = html.Div(children=[
    header,
    html.Div('Placeholder keywords articles')]
    )

layout_keywords_pages = html.Div(children=[
    header,
    html.Div('Placeholder keywords pages')]
    )

layout_keywords_period = html.Div(children=[
    header,
    html.Div('Placeholder keywords period')]
    )

layout_about = html.Div(children=[
    header,
    html.Div('Placeholder About')]
    )

# Add layouts to app

app.validation_layout = html.Div([
    url_bar_and_content_div,
    layout_explore,
    layout_authors_articles,
    layout_authors_pages,
    layout_authors_period,
    layout_keywords_author,
    layout_keywords_articles,
    layout_keywords_pages,
    layout_keywords_period,
    layout_about
])



# Index callbacks
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/explore":
        return layout_explore
    elif pathname == "/authors-articles":
        return layout_authors_articles
    elif pathname == "/authors-pages":
        return layout_authors_pages
    elif pathname == "/authors-period":
        return layout_authors_period
    elif pathname == "/keywords-author":
        return layout_keywords_author
    elif pathname == "/keywords-articles":
        return layout_keywords_articles
    elif pathname == "/keywords-pages":
        return layout_keywords_pages
    elif pathname == "/keywords-period":
        return layout_keywords_period
    elif pathname == "/about":
        return layout_about
    else:
        return layout_explore

# Explore callbacks
@app.callback(
    Output('outbound-link', 'children'),
    Output('outbound-link', 'href'),
    Output('outbound-link', 'title'),
    Output('articleInfo', 'children'),
    Output('pdf-link', 'children'),
    Output('pdf-link', 'href'),
    Output('pdf-link', 'title'),
    Input('articlesByYearFigure', 'clickData'))
def display_click_data(clickData):
    if clickData != None:
        print ('Selected article: '+str(clickData['points'][0]['customdata'][0])+' ('+str(clickData['points'][0]['customdata'][1])+')\n')
        return clickData['points'][0]['customdata'][1], 'https://urn.kb.se/resolve?urn='+ str(clickData['points'][0]['customdata'][1]),clickData['points'][0]['customdata'][0],['Title: ', html.B(children=clickData['points'][0]['customdata'][0]), html.Br(), 'Year: ', html.B(children=clickData['points'][0]['x']), html.Br(), 'Pages: ', html.B(children=clickData['points'][0]['y']), html.Br(), 'Authors: ', html.B(children=clickData['points'][0]['customdata'][3]), html.Br(), 'Keywords:', html.B(children=clickData['points'][0]['customdata'][2]), html.Br(), html.A(children='Open PDF in Voyant Tools', target='_blank', href='http://voyant-tools.org/?input=http://nordiskamuseet.diva-portal.org/smash/get/diva2:'+str(clickData['points'][0]['customdata'][4])+'/FULLTEXT01.pdf&stopList=stop.se.swedish-long.txt&panels=cirrus,reader,trends,summary,contexts')],clickData['points'][0]['customdata'][0],'http://nordiskamuseet.diva-portal.org/smash/get/diva2:'+str(clickData['points'][0]['customdata'][4])+'/FULLTEXT01.pdf',str(clickData['points'][0]['customdata'][0])+' (PDF)'
    else:
        print ('Selected article: None\n')
        return '','','','','','',''

@app.callback(
    Output('articlesByYearFigure', 'figure'),
    Output('articleCount', 'children'),
    Input('keyword', 'value'),
    Input('author', 'value'))
def update_graph(selected_keywords, selected_authors):
    if selected_keywords == 'Keywords' or selected_keywords == None or selected_keywords == []: # all these are versions of "Select all"
        print('Selected keywords: None')
        filteredArticleData = articleData
    else:
        print('Selected keywords:',selected_keywords)
        filteredArticleData = filterByTokens(articleData,selected_keywords,'Keywords')

    if selected_authors == 'Name' or selected_authors == None or selected_authors == []: # all these are versions of "Select all"
        print('Selected authors: None\n')
    else:
        print('Selected authors:',selected_authors,'\n')
        filteredArticleData = filterByTokens(filteredArticleData,selected_authors,'Name')

    fig = px.bar(filteredArticleData, x='Year', y='Pages', hover_data=['Title','NBN','Keywords','Name', 'PID'], barmode = 'stack')
    fig.update_layout(transition_duration=500)
    return fig, str(len(filteredArticleData))+' articles selected'

if __name__ == '__main__': 
    app.run_server(debug=False) 

