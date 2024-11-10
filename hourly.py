from lib.pws_components import  pn, pws_page, site_nav, sidebar_with_station_selection, main_pws_title
from lib.pws_components import  start_date_selector, end_date_selector, station_selector
from lib.pwsapi import get_hourly_readings
import pandas as pd

########## hourly

# station_hourly = pn.bind(get_hourly_readings, station_code = station_selector, start_date = start_date_selector, end_date = end_date_selector)
import json

def station_hourly_pane(station_code, start_date, end_date):    
    hourly_data = get_hourly_readings( station_code = station_code, start_date = start_date, end_date = end_date)
    # if hourly_data:
    #     station_hourly_df = pd.DataFrame.from_records(hourly_data)
    # else:     
    #     station_hourly_df = pd.DataFrame.from_records(hourly_data)
    
    hourly_df = pd.DataFrame.from_records(hourly_data)
    if end_date < start_date:
        main_content = pn.pane.Markdown("**Please select a starting date on or before the end date**")
    else:
        main_content = pn.pane.DataFrame(hourly_df)
            
    return pn.Column(
        pn.Row(pn.Column( start_date_selector),pn.Column( end_date_selector), height = 75),
        pn.Row(main_content)
        
    ) 

def page_title(station_code):
    return f"{main_pws_title}: Hourly Data for {station_selector.value}"

bound_page_title = pn.bind(page_title, station_selector)
    
bound_station_hourly= pn.bind(station_hourly_pane, station_code = station_selector, start_date = start_date_selector, end_date = end_date_selector)

pws_page = pws_page(
    main_pane = bound_station_hourly,
    sidebar = sidebar_with_station_selection(site_nav), 
    page_title = bound_page_title()
)

pws_page.servable()