# pip install CouchDB==0.10
import couchdb
import json


def open_couchdb():
    """open the couchdb through IP address using username and password"""

    with open("couchdb_info.json", 'r') as fp:
        information = json.load(fp)
    fp.close()
    couch = couchdb.Server(information["IP"])

    # add username and password
    couch.resource.credentials = (information["username"],
                                  information["password"])
    return couch


def write_data_to_db(destination, record):
    """
    store new record into destination database

    Keyword arguments:
    destination: database name in CouchDB that we want to use
    record: a JSON file storing information that needs to be writen
    """

    couch = open_couchdb()

    # create a new database if it does not exist
    database_names = [j for j in couch]
    if destination not in database_names:
        db = couch.create(destination)
    else:
        db = couch[destination]
    db.save(record)

