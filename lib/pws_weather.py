from .pwsapi import get_hourly_readings

import pandas as pd

def yesterday_readings(station_code=None):
    """ get a data frame of weather.  When using this in the dash page, use 
    the dash bootstrap component library convenience function
    df = yesterday_readings_table('MYSTATION')
    if df:
        html = dbc.Table.from_dataframe(yesterday_readings_table('MYSTATION'))
    else:
        html = "no readings"
    
    """
    
    if station_code:
        readings = get_hourly_readings(station_code)
        if readings:
            readings_df = pd.DataFrame(readings)

            return(readings_df)
        else:
            return(None)
    else:
        return(None)
