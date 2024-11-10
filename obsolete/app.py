import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
import requests

PRIMARY_COLOR = "#0072B5"
SECONDARY_COLOR = "#B54300"

pn.extension(design="material", sizing_mode="stretch_width")
from lib.pwsapi import get_station_codes, get_station_data
from lib.pws_components import top_row, station_selector




# station_selector = pn.widgets.Select(name = "station_code", value = "EWXDAVIS01", options = list(get_station_codes()))
# start_date = pn.widgets.DatePicker(name="start_date")
# end_date = pn.widgets.DatePicker(name="end_date")

side_bar = pn.WidgetBox('## Menu Of stuff', '### Station Info', "### Station Readings")                          

## station data display
station_data = pn.bind(get_station_data, station_selector)
station_data_pane = pn.pane.JSON(station_data, name='Station')



main_page = pn.template.MaterialTemplate(
    title='EWX Personal Weather Station Data',
    sidebar=[],

)


main_page.append(top_row)

# Append a layout to the main area, to demonstrate the list-like API
from map import station_map
from lib.pwsapi import get_all_stations

stations = get_all_stations()
map_of_stations = pn.bind(station_map,station_selector,stations )
m = map_of_stations()
main_page.main.append(    
    pn.Row(pn.pane.plot.Folium(m, height = 400))
)

main_page.main.append(
    pn.Row(station_data_pane)
)

from lib.pwsapi import get_station_readings

readings_from_station = pn.bind(get_station_readings, )
main_page.main.append(
    pn.Row(bound_plot)
)

main_page.servable()



# @pn.cache
# def get_data():
#   return pd.read_csv(CSV_FILE, parse_dates=["date"], index_col="date")

# data = get_data()

# def transform_data(variable, window, sigma):
#     """Calculates the rolling average and identifies outliers"""
#     avg = data[variable].rolling(window=window).mean()
#     residual = data[variable] - avg
#     std = residual.rolling(window=window).std()
#     outliers = np.abs(residual) > std * sigma
#     return avg, avg[outliers]

# ##### Plot
# def get_plot(variable="Temperature", window=30, sigma=10):
#     """Plots the rolling average and the outliers"""
#     avg, highlight = transform_data(variable, window, sigma)
#     return avg.hvplot(
#         height=300, legend=False, color=PRIMARY_COLOR
#     ) * highlight.hvplot.scatter(color=SECONDARY_COLOR, padding=0.1, legend=False)



# variable_widget = pn.widgets.Select(name="variable", value="Temperature", options=list(data.columns))
# window_widget = pn.widgets.IntSlider(name="window", value=30, start=1, end=60)
# sigma_widget = pn.widgets.IntSlider(name="sigma", value=10, start=0, end=20)



# ### add plot to widgets
# bound_plot = pn.bind(
#     get_plot, variable=variable_widget, window=window_widget, sigma=sigma_widget
# )
