MediaCloud Python API Client Examples
=====================================

This is a set of examples to demonstrate how you can use the MediaCloud API python client
library.

Installation
------------

First [download the latest egg of the python api client module](https://github.com/c4fcm/MediaCloud-API-Client/tree/master/dist) and install it like this:

    easy_install [the egg file]

Now to run these examples make sure you have Python > 2.6 (and setuptools) and then install 
some python modules:
    
    pip install flask
    
Copy the `mc-client.config.template` to `mc-client.config` and edit it, putting in the 
API username and password, and database connection settings too.

Examples
--------

### Web Server

In the `example-web-server` is a simple example of a Flask-based web front end for viewing the data.
Check the README.md in there for more info.
