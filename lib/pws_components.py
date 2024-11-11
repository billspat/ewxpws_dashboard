
# pws_components.py  reuseable components for pages

from lib.pwsapi import get_station_codes, get_station_data
from datetime import date, timedelta

## Config
main_pws_title = 'MSU Enviroweather Personal Weather Station Dashboard'
site_nav = ["map", "station", "hourly", "about"]
sidebar_width = 250


YESTERDAY = date.today() - timedelta(days = 1)
