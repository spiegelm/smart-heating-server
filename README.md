# smart-heating-server [![Build Status](https://magnum.travis-ci.com/spiegelm/smart-heating-server.svg?token=uqu5q9gC3ZDdywezju6y&branch=master)](https://magnum.travis-ci.com/spiegelm/smart-heating-server)

This is the repository for the server part of the Distributed System Laboratory project *An Infrastructure for Smart Residential Heating Systems*:

- [**spiegelm/smart-heating-server**](https://github.com/spiegelm/smart-heating-server)
- [spiegelm/smart-heating-local](https://github.com/spiegelm/smart-heating-local)
- [Octoshape/smart-heating-app](https://github.com/Octoshape/smart-heating-app)
- [spiegelm/smart-heating-report](https://github.com/spiegelm/smart-heating-report)

The server is a RESTful service designed to store and share temperature values and user preferences.

## API design

There are two different API responses for successful GET requests: *resource collections* and *resource representations*.

- **Resource collections and resource representations:** Resource collections list resource representations. Collections are referenced per URL. Resources are referenced by including their representation.

- **URL fields** are identified by the name ``url`` are the suffix ``_url``. Resource representations contain their own URL in the field ``url``.

## Setup instructions

Setup a virtual or dedicated server based on Ubuntu Linux 14.04 LTS and enter the following commands in a terminal:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git python-virtualenv python3-pip
# Install code into home directory
cd ~
git clone https://github.com/spiegelm/smart-heating-server
# Setup virtualenv
virtualenv -p python3 env
. ~/env/bin/activate
# Check for python version >=3.4.0
python --version
# Install requirements, setup database and start server
cd ~/smart-heating-server/
pip install -r requirements.txt
./manage.py migrate
# Run server on port 8000
./manage.py runserver 0.0.0.0:8000
# Test that server is accessible via browser
# Kill server: CTRL-C
```

## Server Management

```bash
# Start server in the background using nohup
./scripts/restart_server.sh
# Kill background server
./scripts/kill_server.sh

# To get the newest code from the repository:
cd ~/smart-heating-server
git pull
./scripts/restart_server.sh
```
