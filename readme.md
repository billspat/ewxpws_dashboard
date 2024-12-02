## Enviroweather Personal Weather Station dashboard

A web dashboard for demonstrating the data and outputs from crop models using the personal weather station (PWS) system.  

This is a work in progress in heavy development.  

It displays data from the data API from the Eniviroweather PWS database as well as the model API (aka RM-API) from Enviroweather. 

### Developers

This is written using the Plotly Dash  

Pages are python files in the main directory.   Other python code is in the `lib` folder. 

To run the app in development mode on your computer: 

- clone or download this project
- create a new file named ".env" with the URLS for enviroweather APIS, based on the contents of "example-dot-env.txt"  
- install a of python  > 3.10 if you do not have python
- It's recommended that you create and activate python environment for each project, for example with pyenv, or virtualenv, or conda
- install required packages listed in the file `requirements-dev.txt` for example with `pip install -r requirements-dev.txt`
  - *note 1: this will also install everything in requirements.txt*
- start a development server to run the website using ...
   - ` `
   - *note the app is under heavy development and the index file may change, omit this parameter if does*
  
- visit the development version of the website on.    


## Run

Dash will use the env variables `PORT` and `HOST`.  This app will use env vars 

- `DASH_TEMPLATE_DIR` html templates, default is `./templates` in app root dir (currently on main.html, not that useful)
- `DASH_CACHE` path to keep the caching for memoizing callbacks, default `./cache_directory` in app root dir

to run the app from any directory, given a virtual environment in `./.venv`, :

```
export APPDIR=$HOME/path/to/ewxpws_dashboard; export HOST='0.0.0.0'; export PORT=8002, export DASH_DEBUG=True; $APPDIR/.venv/bin/python $APPDIR/app.py
```

