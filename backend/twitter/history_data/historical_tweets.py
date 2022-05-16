import mmap
import json
import calendar
import datetime
import re
from CouchDB_functions import *


def reading_compiling_part(map, file_bytes):
    """
    use mmap function to read file with smaller memory and write needed information into CouchDB

    Keyword arguments:
    map: opened map file
    file_bytes: the total bytes in the file to determine EOF
    """

    # get the current position in file
    current_position = map.tell()

    while current_position < file_bytes:

        item = map.readline().decode("utf-8")

        # if arriving the end of file, jump out of the while loop
        if not item:
            break

        # extract last three terms ",\r\n" to satisfy dict format
        if item[:6] == '{"id":' and item[-3:] == ",\r\n":
            json_item = json.loads(item[:-3])

        # the last record has a different ending with others,
        # ("\r\n"), so it needs to be extracted last four terms
        elif item[:6] == '{"id":':
            json_item = json.loads(item[:-2])
        else:
            continue

        # update current position
        current_position = map.tell()

        # compile functions to get tweets information
        content = json_item["doc"]
        language = content["lang"]
        coordinates = content["coordinates"]
        retweeted = content["retweeted"]
        text = content["text"]

        # open the file containing query for topics
        with open("token_and_query.json", 'r') as fp:
            information = json.load(fp)
        fp.close()
        topics = ["environment", "health"]

        for topic in topics:

            # determine whether the tweet is useful
            if (language is not None) and (language != "und") and (retweeted is False) and \
                    (any(keys in text for keys in information["{}_keys".format(topic)])):

                create_time = content["created_at"].split(" ")
                tm = create_time[3].split(":")
                time_output = datetime.datetime(year=int(create_time[-1]),
                                                month=list(calendar.month_abbr).index(create_time[1]),
                                                day=int(create_time[2]),
                                                hour=int(tm[0]),
                                                minute=int(tm[1]),
                                                second=int(tm[2])).strftime("%Y-%m-%dT%H:%M:%SZ")

                # write useful tweets into CouchDB
                if coordinates is not None:
                    coord = coordinates["coordinates"]

                    write_data_to_db("{}_tweets_coordinates".format(topic),
                                     {"_id": content["id_str"], "id": content["id_str"],
                                      "author_id": content["user"]["id"],
                                      "text": content["text"], "lang": content["lang"],
                                      "created_at": time_output, "coordinates": coord})
                write_data_to_db("{}_tweets_text".format(topic),
                                 {"_id": content["id_str"], "id": content["id_str"], "author_id": content["user"]["id"],
                                  "text": content["text"], "lang": content["lang"],
                                  "created_at": time_output})


# use mmap module to read data one by one and collect useful information
with open('twitter-melb.json', 'r', encoding='utf-8') as f:

    # get coordinates and languages
    outer_map = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)

    # count the total bytes in the file
    file_bytes = outer_map.size()

    str_total_rows = outer_map.readline().decode("utf-8")
    total_rows = int(re.findall(r'\"total_rows\":(.*?),', str_total_rows)[0])

    reading_compiling_part(outer_map, file_bytes)
    outer_map.close()
