""" ewx_api.py: functions to work with the Enviroweather RM API in Python
"""


## this goes into the PWS API module

from dotenv import load_dotenv
from datetime import datetime, date
from zoneinfo import ZoneInfo
import requests, json
load_dotenv()
from os import getenv
from pandas import DataFrame


####### MODULE STYLE ##############

#### CONSTANTS
BASE_EWX_API_URL=getenv('ENVIROWEATHER_API_URL', 'https://enviroweather.msu.edu/ewx-api/api')
BASE_EWX_RM_API_URL=getenv('ENVIROWEATHER_API_URL', 'https://enviroweather.msu.edu/rm-api/api')

michigan_time_zone_key = 'US/Eastern'
global current_token_value
current_token_value = None
        
def token_value(base_ewx_api_url = BASE_EWX_API_URL):
    global current_token_value
    if current_token_value is None:
        current_token_value = aquire_token(base_ewx_api_url)
    
    return current_token_value
        
         
def aquire_token(base_ewx_api_url = BASE_EWX_API_URL)->str:
    token_url = f"{base_ewx_api_url}/db2/siteToken"
    r = requests.get(url = token_url)
    if r.status_code == 200:
        request_data:dict = r.json()
        if 'data' in request_data and 'token' in request_data['data']:
            token =request_data["data"]["token"]
            return(token)
    return ""


def get_result_model_keys(base_ewx_api_url:str = BASE_EWX_API_URL):
    """get keys from rm api (currently unused except for testing)"""
    url =  f"{base_ewx_api_url}/db2/resources?type=rm-api"   
    ewx_token = token_value(base_ewx_api_url)
    payload = {}
    
    headers = {
        'Accept': "application/json",
        'Authorization': f"Bearer {ewx_token}"
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    return(response.text)

    
def request_tomcast_api(station_code:str, select_date:datetime|date|None = None, timezone = "America/Detroit", weather:bool = True, base_ewx_rm_api_url:str = BASE_EWX_RM_API_URL, base_ewx_api_url:str = BASE_EWX_API_URL ):
    """hit the tomcast api using the given station_code and date.  If not date is given, find todays date in the given timezone
    Args:
        station_code (str): PWS station code valid from database
        select_date (datetime | date | None, optional): optional date or datetime. Defaults to None.  If none sent, creates current date using timezone sent
        timezone (str, optional): timezone string to use when determine today's date. Only used if no date was sent.  Defaults to Michigan / EasternUS time zone
        weather (bool, optional): ask the api to include weather data with the model output. Defaults to True
        base_ewx_rm_api_url (str, optional): url to use for the rm api (model). Defaults to module constant BASE_EWX_RM_API_URL, which is production api
        base_ewx_api_url (str, optional): url to use for ewx ap to get token. Defaults to module constant BASE_EWX_API_URL, which is production api
    Returns:
        dictionary from api as described by the RM api
    """
    # model params
    station_type:str = "6"  # magic number for all PWS stations
    result_model_code:str = "tomcast"
    
    # allow both datetime and dates 
    if select_date is None:
        # must set timezone explicitly since no guarantee tz of server (or if it's UTC)
        select_date = datetime.now(tz=michigan_time_zone).date()
    elif isinstance(select_date, datetime):
        select_date = select_date.date()
        
    select_date_str = select_date.strftime("%Y-%m-%d")
    
    #example https://enviroweather.msu.edu/rm-api/api/db2/run?stationCode=EWXDAVIS01&stationType=6&selectDate=2024-08-01&resultModelCode=tomcast"

    url = f"{base_ewx_rm_api_url}/db2/run?stationCode={station_code}&stationType={station_type}&selectDate={select_date_str}&resultModelCode={result_model_code}&weather={weather}"    
    ewx_token = token_value(base_ewx_api_url)
    headers = {
        'Accept': "application/json",
        'Authorization': f"Bearer ${ewx_token}"
      }
    payload = {}
    #
    r = requests.request("GET", url, headers=headers, data=payload)
    if r.status_code == 200:
        request_data = r.json()
    else:
        print(f"request error {r.status_code} {r.text} url {url}")
        request_data = {}
    return(request_data)
    

def format_tomcast_model_output(station_code, tomcast_api_output):
    if isinstance(tomcast_api_output, str):
        tomcast_api_output = json.loads(tomcast_api_output)
        
    if 'data' in tomcast_api_output:
        tomcast_data = tomcast_api_output['data']
    else:
        return(DataFrame([{}]))
    
    # get just the basics for now
    tomcast_df = DataFrame(tomcast_data['Table'])
    return(tomcast_df)

        
######### CLASS STYLE ############

# class EwxModelAPI: 
    

#     # class constants    
#     BASE_EWX_API_URL = getenv('ENVIROWEATHER_API_URL', 'https://enviroweather.msu.edu/ewx-api/api')
#     BASE_EWX_RM_API_URL = getenv('ENVIROWEATHER_API_URL', 'https://enviroweather.msu.edu/rm-api/api')
#     michigan_time_zone = ZoneInfo("America/New_York")

#     _current_token_value = ""

#     @classmethod
#     def token(cls):
#         """get current token, request one if needed"""
#         if not cls._current_token_value:
#             cls._current_token_value = cls._request_token(cls.BASE_EWX_API_URL)
            
#         return(cls._current_token_value)
        
#     @classmethod
#     def refresh_token(cls):
#         """used to force update the token if necessary"""
#         cls._current_token_value = cls._request_token()
        
#     @classmethod
#     def _request_token(cls, base_ewx_api_url = BASE_EWX_API_URL)->str:
#         """request a token from the EWX RM-API for use in subsequent API calls"""
#         token_url = f"{base_ewx_api_url}/db2/siteToken"
#         r = requests.get(url = token_url)
#         if r.status_code == 200:
#             request_data:dict = r.json()
#             try:
#                 token = request_data["data"]["token"]
#                 return(token)
#             except KeyError as e:
#                 pass    
#         return ""
    
    
#     def __init__(self, station_code:str, base_ewx_api_url:str = "", api_path = '/api/test'):
        
#         if not base_ewx_api_url:
#             base_ewx_api_url = self.BASE_EWX_API_URL 
        
#         self.api_path = api_path
#         self.station_code = station_code
#         self.base_ewx_api_url = base_ewx_api_url
#         self.station_type:str = "6"  # magic number for all PWS stations
#         self.weather:bool = True 
#         self.last_req_status = None
#         self.last_req_url = None
#         self.last_req_store = None
        
#         # override 
#         result_model_code:str = ""


#     def ewx_headers(self):
#         return {
#             'Accept': "application/json",
#             'Authorization': f"Bearer ${self.token()}"
#             }
    
#     def model_url(self, *args, **kwargs)->str:  # set as a url type from url lie
#         """ craft the URL for this model request OVERRIDE"""
#         tomcast_url = f"{self.base_ewx_api_url}{self.api_path}?stationCode=${self.station_code}&stationType=${self.station_type}"
        
                
#     def make_request(self, request_url)->any:
#         """"makes requests to API and extracts relevant data from model API override""" 
#         self.last_req_url = request_url
#         r = requests.get(headers=self.ewx_headers(), url = request_url)
#         self.last_req_status = r.status_code
#         if r.status_code == 200:
#             request_data = r.json()
#             self.last_req_store = request_data
            
#             return request_data
        
#         # handle errors here
#         return ""
       
#     def model_output(self, request_data)->str:
#         """override - handle request data """
#         return(request_data)
        
        
# class TomcastAPI(EwxModelAPI):
#     """subclass of Model API for tomcast model"""
#     def __init__(self, station_code, base_ewx_api_url= None):        
#         super.__init__(station_code, base_ewx_api_url)
#         self.result_model_code = 'tomcast'
        
#     def model_url(self, select_date, weather=True):        
#         return f"{self.base_ewx_api_url}{self.api_path}?stationCode=${self.station_code}&stationType=${self.station_type}&selectDate=${select_date}&resultModelCode=${self.result_model_code}&weather=${weather}" 
           
#     def make_request(self,select_date, weather=True):
#         r = requests.get(headers=self.ewx_headers(), url = self.model_url(select_date, weather))
#         if r.status_code == 200:
#             request_data = r.json()
#             return request_data
        
#         # handle error here
#         return ""
        

        

    