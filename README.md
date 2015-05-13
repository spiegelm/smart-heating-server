# smart-heating-server [![Build Status](https://magnum.travis-ci.com/spiegelm/smart-heating-server.svg?token=uqu5q9gC3ZDdywezju6y&branch=master)](https://magnum.travis-ci.com/spiegelm/smart-heating-server)

This is the repository for the server part of the Distributed System Laboratory project Smart Heating.

The server is a RESTful service designed to store temperature values and user preferences as well as residence occupancy. This allows to predict the future residence occupancy and therefore estimate the required temperature levels at all times.

## API

There are two different API responses for successful GET requests: *resource collections* and *resource representations*.

- **Resource collections and resource representations:** Resource collections list resource representations. Collections are referenced per URL. Resources are referenced by including their representation.

- **URL fields** are identified by the name ``url`` are the suffix ``_url``. Resource representations contain their own URL in the field ``url``.
