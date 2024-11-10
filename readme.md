## Enviroweather Personal Weather Station dashboard

A web dashboard for demonstrating the data and outputs from crop models using the personal weather station (PWS) system.  

This is a work in progress in heavy development.  

It displays data from the data API from the Eniviroweather PWS database as well as the model API (aka RM-API) from Enviroweather. 

### Developers

This is written using the [panel Python library](https://panel.holoviz.org) from Holoviz.   It is written as a 'multipage' app.   

Pages are python files in the main directory.   Other python code is in the `lib` folder. 

To run the app in development mode on your computer: 

- clone or download this project
- create a new file named ".env" with the URLS for enviroweather APIS, based on the contents of "example-dot-env.txt"  
- install a of python  > 3.10 if you do not have python
- It's recommended that you create and activate python environment for each project, for example with pyenv, or virtualenv, or conda
- install required packages listed in the file `requirements-dev.txt` for example with `pip install -r requirements-dev.txt`
  - *note 1: this will also install everything in requirements.txt*
  - *note 2: the 'watchfiles' package requires Xcode command line tools to be installed on MacOS*
- start a development server to run the website using `panel` using the terminal or cmd in this folder, use the command
   - `panel serve *.py --dev --index map`
   - *note the app is under heavy development and the index file may change, omit this parameter if does*
  
- visit the development version of the website on `http://localhost:5006/about` 



