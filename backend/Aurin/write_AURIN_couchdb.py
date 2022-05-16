from couchdb_functions import *
import os.path

topics = ["environment", "health"]

for i in topics:
    path = "AURIN_{}".format(i)
    if os.path.exists(path):
        files = os.listdir(path)

        for file in files:

            # the structure of "aurin_weather_climate.json" is different, others are same
            with open(path+"/"+file, 'r') as fp:
                full_data = json.load(fp)
            fp.close()
            if file != "aurin_weather_climate.json":
                data = full_data["features"]

                for record in data:
                    useful_record = record["properties"]
                    if "geometry" in record:
                        if record["geometry"]["coordinates"] is not None:
                            useful_record["coordinates"] = record["geometry"]["coordinates"]

                    # write useful_record into CouchDB
                    useful_record["_id"] = record["id"]
                    write_data_to_db(i + "_" + file[:-5], useful_record)

            else:
                for j in list(full_data.keys()):
                    key = str(j)

                    # write useful_record into CouchDB
                    useful_record = full_data[key]
                    useful_record["_id"] = key
                    write_data_to_db(i + "_" + file[:-5], useful_record)
