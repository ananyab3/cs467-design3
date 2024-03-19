import dash
from dash import html, dcc, Input, Output, State
import pandas as pd

# import dash_visual

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def plot_scatterplot(selected_airline, selected_sentiment):
    """
    Creates a scatterplot of Date vs. Number of Tweets.

    Parameters:
    - selected_airline: string containing selected airline name.
    - selected_sentiment: string containing selected sentiment.

    Returns:
    - scatterplot: Plotly figure object representing the heatmap.
    """
    filtered_df = df.copy()
    
    if selected_airline is not None and selected_airline != "All":
        filtered_df = filtered_df[filtered_df['airline'] == selected_airline]
    if selected_sentiment is not None and selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df['airline_sentiment'] == selected_sentiment]
    
    filtered_df['tweet_date'] = pd.to_datetime(filtered_df['tweet_created']).dt.date
    
    tweet_counts = filtered_df['tweet_date'].value_counts().reset_index()
    tweet_counts.columns = ['tweet_date', 'tweet_count']
    
    tweet_counts = tweet_counts.sort_values(by='tweet_date')
    
    fig = px.scatter(tweet_counts, x='tweet_date', y='tweet_count', 
                     labels={'tweet_date': 'Date', 'tweet_count': 'Number of Tweets'},
                     title='Number of Tweets per Day')
    
    return fig


def plot_negative_reasons_heatmap(df):
    """
    Creates a Plotly heatmap of negative reasons by airline from a given DataFrame.

    Parameters:
    - df: pandas.DataFrame containing the dataset with at least 'airline_sentiment',
          'airline', and 'negativereason' columns.

    Returns:
    - fig: Plotly figure object representing the heatmap.
    """
    negative_tweets = df[df['airline_sentiment'] == 'negative']

    negative_reasons_count = negative_tweets.groupby(['airline', 'negativereason']).size().unstack(fill_value=0)

    def get_text_color(cell_value, threshold=300):
        return 'white' if cell_value > threshold else 'black'

    fig = go.Figure(data=go.Heatmap(
        z=negative_reasons_count.values,
        x=negative_reasons_count.columns,
        y=negative_reasons_count.index,
        hoverongaps=False,
        colorscale='Reds',
        colorbar=dict(
            dtick=100 
        )
    ))

    annotations = []
    for yd, airline in enumerate(negative_reasons_count.index):
        for xd, reason in enumerate(negative_reasons_count.columns):
            val = negative_reasons_count.loc[airline, reason]
            annotations.append(
                go.layout.Annotation(
                    text=str(val),
                    x=reason,
                    y=airline,
                    xref='x1',
                    yref='y1',
                    showarrow=False,
                    font=dict(color=get_text_color(val), size=12)
                )
            )

    fig.update_layout(
        autosize=False,
        width=800,
        height=600, 
        title={
            'text': "Heatmap of Negative Reasons by Airline",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title='Reason for Negative Sentiment',
            side='bottom',
            tickangle=-45,
            tickmode='array',
            tickvals=[i for i, _ in enumerate(negative_reasons_count.columns)],
            ticktext=[str(text).replace('_', ' ') for text in negative_reasons_count.columns],
            showgrid=False,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title='Airline',
            autorange='reversed',
            showgrid=False
        ),
        annotations=annotations,
        margin=dict(l=100, r=100, t=100, b=100),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    

    for reason in negative_reasons_count.columns:
        fig.add_shape(
            type='line',
            x0=reason, y0=0, x1=reason, y1=-0.015,
            line=dict(color='black', width=1),
            xref='x', 
            yref='paper'
        )
    
    return fig

def plot_airline_sentiment_barplot(df):
    """
    Creates a Plotly barplot of airline sentiment from a given DataFrame.
    """
    sentiment_counts = df.groupby(['airline', 'airline_sentiment']).size().reset_index(name='counts')
    
    fig = px.bar(
        sentiment_counts, 
        x='airline', 
        y='counts', 
        color='airline_sentiment', 
        title="Domestic Airlines vs. Tweet Sentiments",
    )
    
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
    )
    
    return fig

# Load the dataset.
df = pd.read_csv('dataset/Tweets.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Button('Heatmap', id='heatmap-button', n_clicks=0, className='heatmap-button'),
        html.Button('Barplot', id='barplot-button', n_clicks=0, className='barplot-button'),
        html.Button('Scatterplot', id='scatterplot-button', n_clicks=0, className='scatterplot-button'),
        html.Div(id='dropdowns-container', children=[
            html.Label('Select Airline:', className='airline-dropdown'),
            dcc.Dropdown(
                id='airline-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': airline, 'value': airline} for airline in df['airline'].unique()],
                value='All',
                multi=False
            ),
            html.Label('Select Sentiment:', className='sentiment-dropdown'),
            dcc.Dropdown(
                id='sentiment-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': sentiment, 'value': sentiment} for sentiment in df['airline_sentiment'].unique()],
                value='All',
                multi=False
            ),
        ]),
        html.Div(id='update-scatterplot-container', children=[
            html.Button('Update Scatterplot', id='update-scatterplot-button', n_clicks=0, className='update-scatterplot-button'),
        ], style={'display': 'none'}),
    ]),
    dcc.Graph(id='visual', config={'responsive': True})
])

@app.callback(
    [Output('visual', 'figure'),
     Output('dropdowns-container', 'style'),
     Output('update-scatterplot-container', 'style')],
    [Input('heatmap-button', 'n_clicks'),
     Input('barplot-button', 'n_clicks'),
     Input('scatterplot-button', 'n_clicks'),
     Input('update-scatterplot-button', 'n_clicks')],
    [State('airline-dropdown', 'value'),
     State('sentiment-dropdown', 'value')],
)
def update_visual(heatmap_clicks, barplot_clicks, scatterplot_clicks, update_scatterplot_clicks, selected_airline, selected_sentiment):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'scatterplot-button'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    dropdowns_style = {'display': 'block'}
    update_scatterplot_style = {'display': 'none'}

    if button_id == 'heatmap-button':
        fig = plot_negative_reasons_heatmap(df)
        dropdowns_style = {'display': 'none'}
    elif button_id == 'barplot-button':
        fig = plot_airline_sentiment_barplot(df)
        dropdowns_style = {'display': 'none'}
    elif button_id == 'scatterplot-button':
        fig = plot_scatterplot(selected_airline, selected_sentiment)
        update_scatterplot_style = {'display': 'block'}
    else:
        fig = plot_scatterplot(selected_airline, selected_sentiment)
        update_scatterplot_style = {'display': 'block'}

    return fig, dropdowns_style, update_scatterplot_style

if __name__ == '__main__':
    app.run_server(debug=True)