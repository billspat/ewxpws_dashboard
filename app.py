# PWS Dashboard main entry application
## this pulls data from the API to show station status and data
## based on Plotly Dash
## Version Nov 2024 - Pat Bills

import dash_bootstrap_components as dbc
from dash import ctx, dcc, Dash, html, Input, Output
import dash_ag_grid as dag
import dash_leaflet as dl


## this style sheet helps to style the AG Grid copmonent, courtesy 
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

## set the bootstrap theme here
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc_css])


#### gather station data 

ag_hall_coordinates = [42.73104, -84.47951]
from lib.pwsapi import get_all_stations
station_records = get_all_stations()
station_data = list(station_records.values())


# station_df = pd.DataFrame.from_records(station_data)

# station_lat_lon = [station_data[0]['lat'], station_data[0]['lon']]



#### Selectable Station Table

# only show some fields in the table
station_fields = list(station_data[0].keys())
fields_to_hide = ['id', 'install_date', 'ewx_user_id', 'background_place', 'timezone', 'lat', 'lon', 
                  'api_config', 
                  'expected_readings_day', 
                  'expected_readings_hour', 
                  'first_reading_datetime_utc', 
                  'latest_reading_datetime_utc', 
                  'active']

station_column_defs = [{"field": f} for f in station_fields]
station_column_state = [{"colId": f, "hide": (f in fields_to_hide)} for f in station_fields]


station_table = dag.AgGrid(
    id="station_table",
    rowData=station_data,
    columnDefs=station_column_defs,
    columnState = station_column_state,
    defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth":125},
    columnSize="sizeToFit",
    dashGridOptions={"rowSelection": "single", "cellSelection": False, "animateRows": False},
)



#### STATION MAP

# convenience functions to help show the map and make markers clickable
def station_marker_id(station:dict):
    """consistent way to generate marker id's for us in map and in callbacks"""
    marker_id = f"{station['station_code']}_marker"
    return(marker_id)

def station_from_marker_id(marker_id:str):
    """consistent way to get a station record given a map marker id

    Args:
        marker_id (str): marker id used on a map and returned by a callback fundtion    
        
    Returns:
       str:station code
    """
    
    station_code = marker_id.replace('_marker', '')
    return(station_code)
    
def station_marker(station):
    """generate the marker code for placing stations on the map, 
    extracted into a function for clarity.  calls station_marker_id
    to make consistent ids for use in callbacks

    Args:
        station (dictionary): station record from API, dictionary not pandas

    Returns:
        dash-leaflet.Marker: marker to place on a dash-leaflet maps
    """
    station_description = f"{station['station_code']} ({station['station_type']})"
    return dl.Marker(
        position = [station['lat'],station['lon']],
        children = [dl.Tooltip(content=station_description)], 
        id = station_marker_id(station)
        )

pws_map = dl.Map(id='pws_map',
    children=[
        dl.TileLayer(),
        dl.FeatureGroup( [station_marker(station) for station in station_data], id="station_markers"),
    ],     
    center=ag_hall_coordinates, 
    zoom=13, 
    style={'height': '400px', 'width': '100%'}
    )


#### UI and Layout

navbar_brand_with_logo = [
    html.Img(src = 'assets/davis_station_icon_40px_reverse.png', className = "rounded"),
    html.Span([
        "MSU Enviroweather ", html.Span(" Personal Weather Station Dashboard", style={"padding-left":"2em"})], className = "H3"),    
]
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Weather", href="#")),
        dbc.NavItem(dbc.NavLink("About", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Models", header=True),
                dbc.DropdownMenuItem("TOMCAST", href="#"),
                dbc.DropdownMenuItem("APPLESCAB", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand=navbar_brand_with_logo,
    brand_href="#",
    color="primary",
    dark=True,
    )


header = html.H3(
    "Personal Weather Station Project", className=""
    )

# main_content = html.Div([
#         html.Div(station_table), 
#         html.Div(pws_map),
#         html.Div([html.P(id="text_station_table_selection")]), 
#         html.Div([html.P(id="text_station_map_coordinates")]), 
# ])

# sidebar = [html.Div("sidebar here...")]

app.layout =  dbc.Container([
        navbar,
        dbc.Row([
            html.Div([html.P(id="text_station_table_selection")]), 
        ]),
        dbc.Row([
            dbc.Col(
                station_table,  
                width=6),
            dbc.Col([                
                dbc.Row(pws_map)], 
                width=6),
            ]),
    ],
    fluid=True,
    className="dbc dbc-ag-grid",
)


#### REACTIVITY 

### table row click, delivers a station code for later use
@app.callback(
    Output("text_station_table_selection", "children"),
    Input("station_table", "selectedRows"),
)
def station_table_row_data(row):
    if row is None or row == []:
        return "click a station row"
    # we got a list but just want one
    try:
        row = row[0]
        return f"clicked on row :  {row['station_code']} "  #  row index:   {row['rowIndex']}
    except Exception as e:
        pass


### map marker click
# the output is to select the table row, which then triggers the row click
@app.callback(
        # Output("text_station_map_coordinates", "children"),
        Output("station_table", "selectedRows"),
        [Input(station_marker_id(station), 'n_clicks') for station in station_data],
        prevent_initial_call=True,
        )
def display_marker_click(*args):
    if not ctx.triggered_id:
        return "Click on a station to see details."
    else:
        station_code = station_from_marker_id(ctx.triggered_id)
        # station_record = station_records[station_code]
        return({"function": f"params.data.station_code == '{station_code}'"})            
        # return(station_code, {"function": f"params.data.station_code == '{station_code}'"})            



if __name__ == "__main__":
    # to use debug mode run like this
    # export DASH_DEBUG=True; python app.py
    app.run_server(debug=None, dev_tools_silence_routes_logging = False)