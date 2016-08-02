# Stockholm PyLadies
## Workshop - August 2016

Initial braindump for mentors to walk through

### Initial Requirements

* virtualenv
* freetype2 headers
* libpng headers


### setup

```sh
$ git clone git@github.com:econchick/sto-workshop-2016
$ cd sto-workshop-2016
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ jupyter notebook  # this will open up a browser
```

### layout

#### `notebooks/`

There are two notebooks, which you can browse in the browser that is launched via `jupyter notebook` (or GitHub also renders them nicely, but they are not interactive).

#### `data/`

This is all the raw data that we'll be parsing. It comes from the Meetup API.

#### `src/`

**NOT A PART OF THE TUTORIAL**

This directory is if you don't like looking at Jupyter/IPython Notebooks.

It also is where the script lives to get data from Meetup about Python user groups.  This can be run via:

```sh
python src/main.py getdata --config example.ini
```
