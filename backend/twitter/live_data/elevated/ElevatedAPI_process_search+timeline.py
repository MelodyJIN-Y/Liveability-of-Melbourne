import requests
import json
import copy
import datetime
import time
import re
import os
from CouchDB_functions import *
from multiprocessing import Process
from apscheduler.schedulers.blocking import BlockingScheduler


def json_encoder(objection):
    """store datetime in JSON file as the format of '%Y-%m-%dT%H:%M:%SZ'"""

    if isinstance(objection, datetime.datetime):
        return objection.strftime("%Y-%m-%dT%H:%M:%SZ")


def recent_search_v1(topic):
    """
    Based on the topic, use standard version v1.1 to do recent 7 days search of coordinates in tweets,
    v1.1 can constrain the bonding box according to geographic information

    Keyword arguments:
    topic: one of the two interested topics (environment, health)
    """

    url = "https://api.twitter.com/1.1/search/tweets.json"

    query_params = {'count': 100,
                    'geocode': '-37.81204,144.9624,60km',  # the bounding box of Melbourne
                    'include_entities': 'false'
                    }

    # read token and query from the JSON file
    with open("token_and_query.json", 'r') as fp:
        information = json.load(fp)
    fp.close()
    topic_query = information["Elevated"]["query"][topic]

    headers = {
      'Authorization': 'Bearer {}'.format(information["Elevated"]["{}_token".format(topic)]["Bearer Token"]),
      'Cookie': information["Cookie"]
    }

    query = copy.deepcopy(query_params)
    query["q"] = topic_query

    # update the period that has collected data
    with open("last_time.json", 'r') as fp:
        last_time = json.load(fp)
    fp.close()
    update_last_time = copy.deepcopy(last_time)

    # "Nothing" means the first harvest to collect data in 7 days hasn't started
    # update the json file recording the period that has collected data
    if last_time[topic] != "Nothing":
        update_last_time[topic] = {"start": last_time[topic]["start"],
                                   "end": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    else:
        update_last_time[topic] = {"start": (datetime.datetime.utcnow() +
                                             datetime.timedelta(days=-7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                   "end": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}

    with open("last_time.json", 'w') as fp:
        json.dump(update_last_time, fp, indent=4, default=json_encoder)

    # every time can only collect data from recent 7 days,
    # so collect data until yesterday with interval of 7 days
    query["until"] = (datetime.datetime.utcnow() +
                      datetime.timedelta(days=-1)).strftime("%Y-%m-%d")

    # next_page is True means need to turn pages
    next_page = True

    # Keep turning pages until there is no next page result
    while next_page:
        response = requests.request("GET", url, headers=headers, params=query)

        if response.status_code != 200:
            print("no connection or time out")
            print(response)
            break

        json_response = json.loads(response.text)
        time.sleep(1)

        # skip request that contains empty data
        if "statuses" in json_response and json_response["search_metadata"]["count"] != 0:
            for i in json_response["statuses"]:
                if i["lang"] != "und":
                    if i["coordinates"] is not None:

                        # store coordinates data into CouchDB
                        write_data_to_db("{}_tweets_coordinates".format(topic),
                                         {"_id": i["id"], "id": i["id"], "author_id": i["user"]["id"],
                                          "text": i["text"], "lang": i["lang"], "created_at": i["created_at"],
                                          "coordinates": i["coordinates"]["coordinates"]})

                    # store text data into CouchDB
                    write_data_to_db("{}_tweets_text".format(topic),
                                     {"_id": i["id"], "id": i["id"], "author_id": i["user"]["id"],
                                     "text": i["text"], "lang": i["lang"], "created_at": i["created_at"]})

            # if next page does not have content, stop the while loop
            if "next_results" not in json_response["search_metadata"]:
                next_page = False

            # if next page has content, turn to next page by changing "max_id"
            else:
                query["max_id"] = re.findall(r'max_id=(.*?)&q=', json_response["search_metadata"]["next_results"])

        else:
            print("No data collected")
            break


def user_timeline_v2(topic):
    """
    Based on the topic, search related tweets of users that have posted the same kind of tweets recently

    Keyword arguments:
    topic: one of the two interested topics (environment, health)
    """

    # collect 10 user_ids that posted the most tweets in this topic from CouchDB
    user_id_list = top10_authorid(topic)
    for user_id in user_id_list:
        write_data_to_db("{}_collected_ids".format(topic), {"_id": user_id, "user_id": user_id})
        url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)

        query_params = {'max_results': 100,
                        'tweet.fields': 'id,author_id,text,created_at,lang',
                        'expansions': 'referenced_tweets.id'
                        }

        # read token and query from the JSON file
        with open("token_and_query.json", 'r') as fp:
            information = json.load(fp)
        fp.close()

        headers = {
            'Authorization': 'Bearer {}'.format(information["Elevated"]["{}_token".format(topic)]["Bearer Token"]),
            'Cookie': information["Cookie"]
        }

        with open("last_time.json", 'r') as fp:
            last_time = json.load(fp)
        fp.close()

        # search user timeline from 01/07/2017 to 7 days ago to avoid duplication
        query = copy.deepcopy(query_params)
        query["start_time"] = '2017-07-01T00:00:00Z'
        query["end_time"] = (datetime.datetime.strptime(last_time[topic]["start"], "%Y-%m-%dT%H:%M:%SZ") +
                             datetime.timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # next_page is True means need to turn pages
        next_page = True

        # continue to search until no further results (there is not next page)
        while next_page:
            response = requests.request("GET", url, headers=headers, params=query)

            if response.status_code != 200:
                print("no connection or time out")
                print(response)
                break

            json_response = json.loads(response.text)
            time.sleep(2)

            # skip request that contains empty data
            if "data" in json_response and json_response["meta"]["result_count"] != 0:

                # remove retweeted tweets and keep tweets with text containing keys
                # store valuable data into CouchDB
                for i in json_response["data"]:
                    if "referenced_tweets" in i:
                        types = []
                        for p in i["referenced_tweets"]:
                            types.append(p["type"])
                        if "retweeted" in types:
                            continue
                        elif (any(area in i["text"] for area in information["areas"])) and \
                                i["lang"] != "und" and \
                                (any(keys in i["text"] for keys in information["{}_keys".format(topic)])):
                            write_data_to_db("{}_tweets_text".format(topic),
                                             {"_id": i["id"], "id": i["id"], "author_id": i["author_id"],
                                              "text": i["text"], "lang": i["lang"], "created_at": i["created_at"]})

                    elif (any(area in i["text"] for area in information["areas"])) and \
                            i["lang"] != "und" and \
                            (any(keys in i["text"] for keys in information["{}_keys".format(topic)])):
                        write_data_to_db("{}_tweets_text".format(topic),
                                         {"_id": i["id"], "id": i["id"], "author_id": i["author_id"],
                                          "text": i["text"], "lang": i["lang"], "created_at": i["created_at"]})

                # if next page does not have content, stop the while loop
                if "next_token" not in json_response["meta"]:
                    next_page = False

                # if next page has content, turn to next page by changing "next_token"
                else:
                    query["pagination_token"] = json_response["meta"]["next_token"]

            else:
                print("No data collected")
                break


if __name__ == '__main__':
    """
    run recent_search_v1 functions for two topics simultaneously
    run user_timeline_v2 functions for two topics in order
    use scheduler tool to compile following user_timeline_v2 once a day and recent_search_v1 once a week 
    """

    # create a JSON file to record the time interval of data collected for two topics
    if not os.path.exists("last_time.json"):
        # when the data collection hasn't started, set original values as "Nothing"
        with open("last_time.json", 'w') as file:
            original = {"environment": "Nothing", "health": "Nothing"}
            json.dump(original, file, indent=4)

    # run two recent search functions together
    search_proc1 = Process(target=recent_search_v1, args=("environment",))
    search_proc1.start()
    search_proc2 = Process(target=recent_search_v1, args=("health",))
    search_proc2.start()
    search_proc1.join()
    search_proc2.join()

    # run two timeline functions
    user_timeline_v2("environment")
    user_timeline_v2("health")

    # compile functions at certain intervals
    # if the task is missed within one hour, also need to execute it (misfire_grace_time is 3600 seconds)
    scheduler = BlockingScheduler()
    scheduler.add_job(func=user_timeline_v2, args=["environment"], trigger='interval', days=1, misfire_grace_time=3600)
    scheduler.add_job(func=user_timeline_v2, args=["health"], trigger='interval', days=1, misfire_grace_time=3600)
    scheduler.add_job(func=recent_search_v1, args=["environment"], trigger='interval', days=7, misfire_grace_time=3600)
    scheduler.add_job(func=recent_search_v1, args=["health"], trigger='interval', days=7, misfire_grace_time=3600)
    scheduler.start()

