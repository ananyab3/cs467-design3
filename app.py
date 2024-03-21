from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go 
from shinywidgets import output_widget, render_widget
from datetime import datetime

from ipywidgets import widgets, interactive, Output

df = pd.read_csv("data/202301-divvy-tripdata.csv")

app_ui = ui.page_fluid(
    ui.panel_title("Portrait of Cyclistic's Users"),
    ui.navset_pill(  
    ui.nav_panel("Distribution of Bike Types", output_widget("bike_types")),
    ui.nav_panel("Distribution of Ride Times", output_widget("ride_times")),
    ui.nav_panel("Start Stations", output_widget("start_stations", width="100%", height="1000px")),
    ui.nav_panel("End Stations", output_widget("end_stations", width="100%", height="1000px")),
    id="tab",  
)
)


def server(input, output, session):
    @render_widget
    def bike_types():
        bike_counts = df.groupby(['rideable_type', 'member_casual']).size().unstack(fill_value=0)
        bike_counts.index = [x.replace('_', ' ').title() for x in bike_counts.index]

        colors = {
            'Casual': '#CBC3E3',  
            'Member': '#95D5B2'  
        }
        fig = go.Figure()
        for user_type in bike_counts.columns:
            fig.add_trace(go.Bar(
                name=user_type.title(),  
                y=bike_counts.index,  
                x=bike_counts[user_type],
                orientation='h',  
                marker_color=colors[user_type.title()],  
                hoverinfo='x+name'  
            ))
        fig.update_layout(
            barmode='stack',
            title={
                'text': 'Distribution of Member Types by Bike Types',
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24}
            },
            yaxis=dict(
                title='Bike Type',
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title='Ride Count',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend_title=dict(
                text='Member Type',
                font_size=16
            ),
            legend=dict(
            x=1.05,  
            xanchor='left',  
            y=1,
            bgcolor='rgba(255, 255, 255, 0.5)', 
            bordercolor='Black', 
        ),
            autosize=False,
            width=800,
            height=600,
            margin=dict(l=100, r=100, t=100, b=100),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        return fig
    @render_widget
    def ride_times():
        df['started_at'] = pd.to_datetime(df['started_at'])
        df['ended_at'] = pd.to_datetime(df['ended_at'])
        df['ride_duration'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
        bins = [0, 10, 30, 60, float('inf')]
        bin_labels = ['<10', '10-30', '31-59', '60+']
        df['ride_time_category'] = pd.cut(df['ride_duration'], bins, labels=bin_labels, right=False)
        time_counts = df.groupby(['ride_time_category', 'member_casual']).size().unstack(fill_value=0)
        time_percentages = time_counts.divide(time_counts.sum(axis=1), axis=0)

        fig = go.Figure()

        for member_type, color in zip(time_percentages.columns, ['#F1C40F', '#239B56']):
            fig.add_trace(go.Bar(
                y=time_percentages.index,
                x=time_percentages[member_type],
                name=member_type,
                orientation='h',
                marker=dict(
                    color=color,
                    line=dict(color='rgba(58, 71, 80, 1.0)', width=0.5)
                )
            ))

        fig.update_layout(
            barmode='stack',
            title='Distribution of Member Types and Ride Times',
            xaxis=dict(
                title='% of Rides',
                tickvals=[i/100 for i in range(0, 101, 10)],
                ticktext=[f'{i}%' for i in range(0, 101, 10)]
            ),
            yaxis=dict(
                title='Ride Time (in mins)'
            )
        )
        return fig
    @render_widget
    def start_stations():
        df.dropna(subset=['start_station_name', 'start_station_id'], inplace=True)
        df['started_at'] = pd.to_datetime(df['started_at'])
        fig = px.scatter_mapbox(df, lat='start_lat', lon='start_lng',
                                hover_name='start_station_name', hover_data=['ride_id', 'rideable_type'],
                                color='rideable_type', zoom=10)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=800)
        return fig
    @render_widget
    def end_stations():
        df.dropna(subset=['end_station_name', 'end_station_id'], inplace=True)
        df['ended_at'] = pd.to_datetime(df['ended_at'])
        fig = px.scatter_mapbox(df, lat='end_lat', lon='end_lng',
                                hover_name='end_station_name', hover_data=['ride_id', 'rideable_type'],
                                color='rideable_type', zoom=10)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=800)
        return fig


app = App(app_ui, server)