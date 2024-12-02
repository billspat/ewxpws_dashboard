"""converters.py

simple functions to help with unit conversions

None of these are rounded  - setting the precision is the job
of the calling program 
"""

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
    
