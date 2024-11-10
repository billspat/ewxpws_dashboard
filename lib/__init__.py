##### load system configuration from config file

from dotenv import load_dotenv
from os import getenv
load_dotenv()

BASE_PWS_API_URL = getenv('BASE_PWS_API_URL')
