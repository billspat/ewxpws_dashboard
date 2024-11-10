# map.py page with map and selector
from lib.pws_components import pn, station_map, pws_page, site_nav, sidebar_with_station_selection,main_pws_title, station_selector, station_data_pane
from lib.pwsapi import get_all_stations
bound_map_of_stations = pn.bind(station_map, selected_station_code = station_selector, stations = get_all_stations() )
bound_station_data_pane = pn.bind(station_data_pane, station_selector)

map_pane = pn.Column(
                pn.Row(
                    pn.Column(pn.pane.plot.Folium(bound_map_of_stations, sizing_mode='stretch_both'),
                        height_policy = 'max', 
                        width_policy='max'
                    ), 
                    pn.Column(bound_station_data_pane)
                )
            ) 


map_page = pws_page(
    main_pane = map_pane,
    sidebar = sidebar_with_station_selection(site_nav), 
    page_title = main_pws_title
)

map_page.servable()
