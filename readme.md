## Enviroweather Personal Weather Station dashboard

A web dashboard for demonstrating the data and outputs from crop models using the personal weather station (PWS) system.  

This is a work in progress in heavy development.  

It displays data from the data API from the Eniviroweather PWS database as well as the model API (aka RM-API) from Enviroweather. 

### Developers

This is written using the Plotly Dash  

Pages are python files in the main directory.   Other python code is in the `lib` folder. 

To run the app in development mode on your computer: 

- active internet connection to access PWS and Enviroweather APIs
- clone or download this project
- create a new file named ".env" with the URLS for enviroweather APIS, based on the contents of "example-dot-env.txt"  
- install a of python  > 3.10 if you do not have python
- It's recommended that you create and activate python environment for each project, for example with pyenv, or virtualenv, or conda
- install required packages listed in the file `requirements-dev.txt` for example with `pip install -r requirements-dev.txt`
  - *note 1: this will also install everything in requirements.txt*
- start a development server to run the website using `python app.py` which starts the python (Flask) application on 
  localhost ( 127.0.0.1 ) with the port set in the `.env` file, currently 5006
- open browser on http://127.0.0.1:5006/ to visit the development version of the website on.    


## Run

Dash will use the env variables `PORT` and `HOST`.  This app will use env vars 

- `DASH_TEMPLATE_DIR` html templates, default is `./templates` in app root dir (currently on main.html)
- `DASH_CACHE` path to keep the caching for memoizing callbacks, default `./cache_directory` in app root dir

to run the app from any directory, given a virtual environment in `./.venv`, :

```
export APPDIR=$HOME/path/to/ewxpws_dashboard; export HOST='0.0.0.0'; export PORT=8002; export DASH_DEBUG=True; $APPDIR/.venv/bin/python $APPDIR/app.py
```

## Updating Station Data

Data on the page is updated when a new station is selected if the data has 
been updated in the database from the data collection process (currently this 
takes place on the server every 30 minutes so 5 minute data is not automatically 
updated  - that is a different issue)

However, ff he station data in the database is updated, **this app must be restarted to 
show changes in the station table**.   
The tech solution to avoid this is beyond the scope of this
temporary interface. 

Plotly Dash by nature does not automatically update data from external sources
and requires adding a counter element to force updates. 

The row in station table would be unselected when updates happened so the 
station list table itself is not updated from latest API/database table. 

see issue #20 in gitlab for more details.  