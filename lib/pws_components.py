
import panel as pn
import folium
from lib.pwsapi import station_latlon, get_all_stations, get_hourly_readings

pn.extension(loading_spinner='dots', loading_color='#00aa41', sizing_mode="stretch_both")  #  template='bootstrap',

# pn.extension(design="material", sizing_mode="stretch_both")

from lib.pwsapi import get_station_codes, get_station_data

## Config
main_pws_title = 'MSU Enviroweather Personal Weather Station Dashboard'
site_nav = ["map", "station", "hourly", "about"]
sidebar_width = 250


## widgets
station_selector = pn.widgets.Select(name = "station_code", 
                                     value = "", 
                                     options = list(get_station_codes()),
                                     width = sidebar_width-25, height = 50)


if pn.state.location:
    pn.state.location.sync(station_selector, {'value': 'station_code'})


from datetime import date, timedelta
YESTERDAY = date.today() - timedelta(days = 1)
start_date_selector = pn.widgets.DatePicker(name="start_date", end = date.today(), value = YESTERDAY)
end_date_selector = pn.widgets.DatePicker(name="end_date",end = date.today(), value = date.today())


######## Station selection and parameters
top_row = pn.Row(
    pn.Column( station_selector),
    pn.Column( start_date_selector),
    pn.Column( end_date_selector)
)

######### sidebar content 
def links_pane(links):    
    markdown_links = [f"- [{link}]({link})" for link in links]
    links_pane = pn.pane.Markdown("\n".join(markdown_links))
    
    return(links_pane)


def sidebar_with_nav(links):
    """just a column of links """

    return(
        pn.Column(links_pane(links))
    )


def nav_pane(links):
    """local and external links """
    
    affliate_links = """
---

**[MSU Enviroweather](https://enviroweather.msu.edu)**    

"""

    return(
        pn.Column(
            links_pane(links),
            pn.pane.Markdown(affliate_links))
        )

def sidebar_with_station_selection(links):
    """column with a station selector followed by links"""
    sidebar_column = [
            pn.Row(station_selector, height = 75), 
            nav_pane(links)
            ]
    
    return(sidebar_column)



############# station data
# station_data = pn.bind(get_station_data, station_selector)

import pandas as pd

def station_data_pane(station_code):
    station_data = get_station_data(station_code)
    station_data_table = pd.DataFrame.from_dict(station_data, orient='index')    
    return pn.pane.DataFrame(station_data_table, name='Station')


 
# bound_station_data_pane = pn.bind(station_data_pane,station_code = station_selector )   
########## Map

def station_map(selected_station_code, stations, starter_location = [42.71025, - 84.46308]):
    
    # if(selected_station_code):
    #     starter_location  = station_latlon(selected_station_code)
        
    m = folium.Map(location = starter_location, zoom_start=15)
    
    for station_code in stations:
        
        station = stations[station_code]        
        station_link = f"click to see <a target=\"_parent\" href=\"/station\">{station_code}</a> {station.get('station_type')}" 
        station_coordinates = [station.get('lat'),station.get('lon')]
        
        marker_color = 'red' if (selected_station_code == station_code) else 'green' 
        
        marker = folium.Marker(
            station_coordinates, 
            popup = station_link, 
            icon=folium.Icon(color=marker_color)
            )    
        
        # marker = folium.Marker(
        #     station_coordinates, 
        #     popup = station.get('station_location'), 
        #     tooltip = station_info,
        #     icon=folium.Icon(color=marker_color)
        #     )
                
        marker.add_to(m)
        
        # set map location 
        if(selected_station_code and selected_station_code == station_code):            
            m.location = station_coordinates
    
        
    return(m)

    

###### 
def pws_page(main_pane:pn.pane, sidebar:pn.Column, page_title:str)->pn.template: 
    """page generator with standard layout

    Args:
        main_pane (pn.pane): a pn pane with content to display
        sidebar (pn.Column): _description_
        page_title (str): _description_

    Returns:
        pn.template: _description_
    """
    page = pn.template.BootstrapTemplate(
        title= page_title,
        sidebar=sidebar,
        sidebar_width=sidebar_width, 
        header_background = "#18453b"
    )
    
      
    # page.main.append(top_row)
    page.main.append( main_pane)
    
    return page                
              
  
