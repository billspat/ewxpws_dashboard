
import lib.pws_components as pws_components

about_text = """

### About the Enviroweather Personal Weather Station (PWS) Project

The Enviroweather Personal Weather Station (PWS) Project is...

- Groovy
- Complicated
- Grower-focused

This dashboard is primarily for internal use to monitor 

*This project was funded by project GREEEN from Michigan Ag-Bio Research and the MSU College of Agriculture and Natural Resources*
"""


about_pane = pws_components.pn.pane.Markdown(about_text)
about_page = pws_components.pws_page(main_pane = about_pane, 
                                   sidebar = pws_components.sidebar_with_nav(pws_components.site_nav), 
                                   page_title = pws_components.main_pws_title
                                   )
about_page.servable()



#     "map": , 
#     "station": pws_page(main_pane = pn.pane.Markdown("## station data here"), links = site_nav,  page_title = main_pws_title),
#     "about": pws_page(main_pane = pn.pane.Markdown("### about page"), links = site_nav,  page_title = main_pws_title)
