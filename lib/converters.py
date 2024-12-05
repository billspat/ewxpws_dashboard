"""converters.py

simple functions to help with unit conversions

None of these are rounded  - setting the precision is the job
of the calling program 
"""

from datetime import time, datetime, date, timedelta
from zoneinfo import ZoneInfo

MICHIGAN_TIME_ZONE_KEY = 'US/Eastern'
MICHIGAN_TIME_ZONE = ZoneInfo(MICHIGAN_TIME_ZONE_KEY)

    
def today_localtime(timezone_key = MICHIGAN_TIME_ZONE_KEY  ):
    """server TZ is UTC, so get the date of the day in stations' timezone
    """
    return datetime.now(tz=ZoneInfo(timezone_key)).date()
    
def today_localtime_str(timezone_key = MICHIGAN_TIME_ZONE_KEY):
    """server TZ is UTC, so get the date of the day in 
    stations' timezone as a string YYYY-MM-DD
    """
    return today_localtime(timezone_key).strftime("%Y-%m-%d")

def days_ago(d:int, timezone_key = MICHIGAN_TIME_ZONE_KEY):
    """ using local timezone, give date some days ago"""

    return (datetime.now(tz=ZoneInfo(timezone_key)) - timedelta(days = d)).date()



def first_of_year_string():
    """get the current year and Jan 1st to limit dates to this year"""
    this_year = today_localtime().year
    return date(this_year, 1,1).strftime("%Y-%m-%d")

    
def c2f(c:float)->float:
    """ centigrate to fahrenheit
    """
    f = c*(9/5) + 32
    return(f)

def mm2inch(mm:float)->float:
    """ millimieters to inches
    """
    inches = mm / 25.641
    return(inches)

def kph2mph(kph:float)->float:
    """convert kilometers per hour to miles per hour, used for 
    wind speed

    Args:
        kph (float): kilometers per hour

    Returns:
        float: miles per hour
    """
    
    mph = kph * 0.6213712
    return( mph ) 
    
def degree2compass(deg:float)->str:
    """convert decimal degress to compass points from 16 point compass

    Args:
        deg (float): decimal degrees
    
    Returns:
        str: compass direction abbreviation
    """
    
    directions = [
    'N', 'NNE', 'NE', 'ENE',
    'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW',
    'W', 'WNW', 'NW', 'NNW',
    ] 
    
    if deg == 0.0:
        return('calm')
    
    points = 16    
    width = 360/points
    direction_index:int =  int((deg + width/2)/width) % 16
    
    direction:str = directions[direction_index]
    
    return(direction)
    
    
def hour_number2clock_str(h:int)->str:
    """convert the hour number ( 1 to 24) which is output by hourly
    weather summary into a human readable time interval
    
    hour 1 => '12:00AM-12:59AM'

    Args:
        h (int): hour number 1 is first hour of the day

    Returns:
        str: time interval in 12hr clock
    """
    
    # try:
    #     h = int(h)
    # except Exception as e:
    #     return ""
    
    #h = int(h)
    if (h > 24) or (h < 1):
        return("")
    
    start_time = time((h-1),0)
    end_time = time(start_time.hour, 59)
    time_interval_str = start_time.strftime("%I:%M") + "-" + end_time.strftime("%I:%M %p")
    
    return(time_interval_str)    