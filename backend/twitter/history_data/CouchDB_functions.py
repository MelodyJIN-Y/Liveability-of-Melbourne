# pip install CouchDB==0.10
import couchdb
import json


def open_couchdb():
    """open the couchdb through IP address using username and password"""

    with open("token_and_query.json", 'r') as fp:
        information = json.load(fp)
    fp.close()

    option = 0
    couch = None

    # try to connect to CouchDB through three provided IPs until connecting successfully
    while couch is None:
        try:
            # connected to CouchDB
            couch = couchdb.Server(information["CouchDB"]["IP"][option])

        # if the connection fails, change options among [0, 1, 2] iteratively
        except:
            if option == 2:
                option = 0
            else:
                option += 1
            pass

    # add username and password
    couch.resource.credentials = (information["CouchDB"]["username"],
                                  information["CouchDB"]["password"])
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

    # check whether the tweet ID has collected in the database
    # only save tweets with tweet IDs not collected (unique "_id")
    try:
        db.save(record)
    except:
        pass


def top10_authorid(topic):
    """
    Based on the topic, sort the appearances of unique authors in descending order,
    and collect the list of authors in descending order

    Keyword arguments:
    topic: one of the two interested topics (environment, health)

    Return:
    a list of top-10 author ids that posted the most related tweets
    """

    couch = open_couchdb()

    # if the "collected_ids" database hasn't been created,
    # directly find top 10 author_ids. Otherwise, need to
    # check whether the author_id has been collected ever
    database_names = [j for j in couch]
    if "{}_collected_ids".format(topic) not in database_names:
        collected_ids = []
    else:
        db = couch["{}_collected_ids".format(topic)]
        unique_id = db.view('_design/user_id/_view/unique_id', reduce=True, group=True, descending=True)
        collected_ids = [p.key for p in unique_id]

    database = couch["{}_tweets_text".format(topic)]
    top_author_id = []

    # do map reduce process
    counts = database.view('_design/author_id/_view/count_author', reduce=True, group=True, descending=True)

    top_ten = 0
    for i in counts:
        key = i.key
        if key not in collected_ids:
            top_author_id.append(key)
            top_ten += 1
        if top_ten == 10:
            break
    return top_author_id


def add_view(db_name, design_name, view_name, map_key, reduce):
    """
    add a view into CouchDB for further MapReduce

    Keyword arguments:
    db_name: database name in CouchDB
    design_name: the name want to give under _design directory
    view_name: the name want to give for the view
    map_key: the key feature(s) in map function
    reduce: reduce function want to apply after map function
    """

    map_reduce = {
        "_id": "_design/{}".format(design_name),
        "views": {
            view_name: {
                "reduce": reduce,
                "map": "function (doc) {" + "\n  emit(doc.{}, 1);".format(map_key) + "\n}"
            }
        },
        "language": "javascript"
    }

    write_data_to_db(db_name, map_reduce)


def delete(db):
    """delete the database (db)"""

    del db
    print("delete successfully")


# add_view("environment_tweets_text", "id_test", "count_test", "author_id", "_count")
