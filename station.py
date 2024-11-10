# map.py page with map and selector
from lib.pws_components import pn, pws_page, station_data_pane, main_pws_title, sidebar_with_station_selection, site_nav,station_selector

station_sidebar = sidebar_with_station_selection(site_nav)
bound_station_data_pane = pn.bind(station_data_pane, station_selector)

station_page = pws_page(
    main_pane = bound_station_data_pane,
    sidebar = station_sidebar,
    page_title = main_pws_title
)

station_page.servable()