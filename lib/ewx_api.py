""" ewx_api.py: functions to work with the Enviroweather RM API in Python
"""

from dotenv import load_dotenv
load_dotenv()
import requests
from os import getenv

BASE_EWX_API_URL=getenv('ENVIROWEATHER_API_URL', 'https://enviroweather.msu.edu/ewx-api/api')

def get_token(base_ewx_api_url = BASE_EWX_API_URL)->str:
    token_url = f"{base_ewx_api_url}/db2/siteToken"
    r = requests.get(url = token_url)
    if r.status_code == 200:
        payload:dict = r.json()
        try:
            token =payload["data"]["token"]
            return(token)
        except KeyError as e:
            pass    
    return ""