import time
import datetime
import requests
import json
import copy
from CouchDB_functions import *
from multiprocessing import Process


def recent_search_v2(topic):
    """
    Based on the topic, search tweets in recent 7 days

    Keyword arguments:
    topic: one of the two interested topics (environment, health)
    """

    url = "https://api.twitter.com/2/tweets/search/recent"

    query_params = {'max_results': 100,
                    'tweet.fields': 'id,author_id,text,created_at,lang'
                    }

    # read token and query from the JSON file
    with open("token_and_query.json", 'r') as fp:
        information = json.load(fp)
    fp.close()

    headers = {
        'Authorization': 'Bearer {}'.format(information["Essential"]["{}_token".format(topic)]["Bearer Token"]),
        'Cookie': information["Cookie"]
    }

    # '-is:retweet' is to not match on Retweets, thus matching only on original Tweets
    topic_query = information["Essential"]["query"][topic]

    query = copy.deepcopy(query_params)
    query["query"] = topic_query

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
        time.sleep(1)

        # skip request that contains empty data
        if "data" in json_response and json_response["meta"]["result_count"] != 0:

            # store useful data into CouchDB
            for record in json_response["data"]:
                if record["lang"] != "und":
                    record["_id"] = record["id"]
                    write_data_to_db("{}_tweets_text".format(topic), record)

            # if next page does not have content, stop the while loop
            if "next_token" not in json_response["meta"]:
                next_page = False

            # if next page has content, turn to next page by changing "next_token"
            else:
                query["next_token"] = json_response["meta"]["next_token"]

        else:
            print("No data collected")
            break


def stream(topic):
    """
    Based on topic, do version 2 stream to get the latest records continuously

    Keyword arguments:
    topic: one of the two interested topics (environment, health)
    """

    url = "https://api.twitter.com/2/tweets/search/stream"
    query_params = {'tweet.fields': 'id,author_id,text,created_at,lang',
                    }

    # read token and query from the json file
    with open("token_and_query.json", 'r') as fp:
        information = json.load(fp)
    fp.close()

    headers = {
        'Authorization': 'Bearer {}'.format(information["Essential"]["{}_token".format(topic)]["Bearer Token"]),
        'Cookie': information["Cookie"]
    }

    response = requests.request("GET", url, headers=headers, params=query_params, stream=True)

    if response.status_code != 200:
        print("no connection or time out")
        print(response)

    # store useful data into CouchDB
    try:
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)

                if "data" in json_response:
                    # skip retweeted tweets and store satisfied tweets into CouchDB
                    if json_response["data"]["text"][:2] != "RT" and json_response["data"]["lang"] != "und":
                        written_data = json_response["data"]
                        written_data["_id"] = json_response["data"]["id"]
                        write_data_to_db("{}_tweets_text".format(topic), written_data)
    except:
        pass


if __name__ == '__main__':
    """run recent_search_v2 and stream functions simultaneously for two topics"""

    # run two recent search functions together
    search_proc1 = Process(target=recent_search_v2, args=("environment",))
    search_proc1.start()
    search_proc2 = Process(target=recent_search_v2, args=("health",))
    search_proc2.start()
    search_proc1.join()
    search_proc2.join()

    # run two stream functions together
    stream_proc1 = Process(target=stream, args=("environment",))
    stream_proc1.start()

    stream_proc2 = Process(target=stream, args=("health",))
    stream_proc2.start()

    stream_proc1.join()
    stream_proc2.join()

