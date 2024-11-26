

#### STATION MAP
# convenience functions to help show the map and make markers clickable

import dash_leaflet as dl

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


def station_map(station_records, map_zoom = 7, center_coordinates = None):
    station_data = list(station_records.values())
    
    selected_station_id = 0
    if not center_coordinates:
        center_coordinates = [station_data[selected_station_id]['lat'], station_data[selected_station_id]['lon']]
        
    m = dl.Map(
        id='station_map',        
            children=[
                dl.TileLayer(),
                dl.FeatureGroup( [station_marker(station) for station in station_data], id="station_markers"),
            ],     
            center=center_coordinates,
            className = "w-100", 
            style={'height': '400px', 'width': '100%'},  
            zoom=map_zoom ,
            invalidateSize = True         
        )

    return(m)

