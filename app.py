from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from shinywidgets import output_widget, render_widget
from datetime import datetime

from ipywidgets import widgets, interactive, Output

df = pd.read_csv("data/202301-divvy-tripdata.csv")

app_ui = ui.page_fluid(
    ui.panel_title("Portrait of Cyclistic's Users"),
    ui.navset_pill(  
    ui.nav_panel("Distribution of Bike Types", "hi"),
    ui.nav_panel("Distribution of Ride Times", ui.output_plot("ride_times")),
    ui.nav_panel("Start Stations", output_widget("start_stations", width="100%", height="1000px")),
    ui.nav_panel("End Stations", output_widget("end_stations", width="100%", height="1000px")),
    id="tab",  
)
)


def server(input, output, session):
    @render.plot
    def ride_times():
        df['started_at'] = pd.to_datetime(df['started_at'])
        df['ended_at'] = pd.to_datetime(df['ended_at'])
        df['ride_duration'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
        bins = [0, 10, 30, 60, float('inf')]
        bin_labels = ['<10', '10-30', '31-59', '60+']
        df['ride_time_category'] = pd.cut(df['ride_duration'], bins, labels=bin_labels, right=False)
        time_counts = df.groupby(['ride_time_category', 'member_casual']).size().unstack(fill_value=0)
        time_percentages = time_counts.divide(time_counts.sum(axis=1), axis=0)
        fig, ax = plt.subplots(figsize=(12, 6))
        time_percentages.plot(kind='barh', stacked=True, ax=ax, color=['#F1C40F', '#239B56'])
        ax.set_ylabel('Ride Time (in mins)', fontsize=12)
        ax.set_xlabel('% of Rides', fontsize=12)
        ax.set_title('Distribution of Member Types and Ride Times', fontsize=14)
        ax.set_xticks([i/100 for i in range(0, 101, 10)])
        ax.set_xticklabels([f'{i}%' for i in range(0, 101, 10)])
        for n, x in enumerate([*time_percentages.index.values]):
            for (proportion, x_loc) in zip(time_percentages.loc[x],
                                        time_percentages.loc[x].cumsum()):
                ax.text(x=(x_loc - proportion) + (proportion / 2),
                        y=n,
                        s=f'{proportion * 100:.1f}%',
                        color="black",
                        fontsize=10,
                        fontweight="bold",
                        va='center')
        ax.legend(title='Member Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
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
