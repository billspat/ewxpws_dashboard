"""converters.py

simple functions to help with unit conversions

None of these are rounded  - setting the precision is the job
of the calling program 
"""

from datetime import time

def c2f(c:float)->float:
    f = c*(9/5) + 32
    return(f)

def mm2inch(mm:float)->float:
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