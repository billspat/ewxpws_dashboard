# map.py page with map and selector
from lib.pws_components import  pn, pws_page, site_nav, sidebar_with_station_selection, main_pws_title

meteogram_hold_content = """
## Meteogram

This page under development

"""
map_page = pws_page(
    main_pane = pn.pane.Markdown(meteogram_hold_content),
    sidebar = sidebar_with_station_selection(site_nav), 
    page_title = main_pws_title
)

map_page.servable()