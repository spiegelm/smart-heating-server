# smart-heating-server [![Build Status](https://magnum.travis-ci.com/spiegelm/smart-heating-server.svg?token=uqu5q9gC3ZDdywezju6y&branch=master)](https://magnum.travis-ci.com/spiegelm/smart-heating-server)

This is the repository for the server part of the Distributed System Laboratory project Smart Heating.

The server is a RESTful service designed to store temperature values and user preferences as well as residence occupancy. This allows to predict the future residence occupancy and therefore estimate the required temperature levels at all times.

## API

There are two different API responses for successful GET requests: *resource collections* and *resource representations*.

- **Resource collections and resource representations:** Resource collections list resource representations. Collections are referenced per URL. Resources are referenced by including their representation.

- **URL fields** are identified by the name ``url`` are the suffix ``_url``. Resource representations contain their own URL in the field ``url``.

## Setup instructions

Setup a virtual or dedicated server based on Ubuntu Linux 14.04 LTS and enter the following the commands in a terminal:

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-virtualenv
sudo apt-get install git
cd ~
git clone https://github.com/spiegelm/smart-heating
cd smart-heating/
git checkout server
cd ~
virtualenv -p python3 env
sudo apt-get install python3-pip
source env/bin/activate
python --version
cd smart-heating/server/
pip install -r requirements.txt
python manage.py migrate
python ./manage.py runserver 0.0.0.0:8000 # run server on port 8000
```
