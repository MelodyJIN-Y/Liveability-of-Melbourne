from typing import Counter
import couchdb
import requests
import json
from collections import Counter
import geopandas
import pandas as pd
import matplotlib.pyplot as plt
from shapely import geometry
import folium
import mapclassify

# convert dicts into Counters, merge then return dict
def concat_lists_of_dicts(ls1, ls2):
    ls1_dict = {ls1[i]['key']: ls1[i]['value'] for i in range(len(ls1))}
    ls2_dict = {ls2[i]['key']: ls2[i]['value'] for i in range(len(ls2))}

    new_dict = Counter(ls1_dict) + Counter(ls2_dict)


    return dict(new_dict)

# retrieve coordinate data
def get_coords(db_name):
    # connect to couch db
    with open("./static/token.json", 'r') as fp:
        info = json.load(fp)
    fp.close()

    username = info["CouchDB"]["username"]
    password = info["CouchDB"]["password"]
    option = 0
    ip = info["CouchDB"]["IP"][option]
    url = f"http://{username}:{password}@{ip}{db_name}/_design/coordinate/_view/view?group_level=2"

    result = []
    try:
        response = requests.get(url)
        result = json.loads(response.text)['rows']
    except:
        print('url not retrievable')
        if option == 2:
            option = 0
        else:
            option += 1
        pass

    
    return result


# produce a geojson file that only contains lgas of the greater Melbourne which is of the interest in this project
# this should be done before calling draw_choropleth(), but this only requires to be done once
def filter_lgas():
    gdf = geopandas.read_file('./static/vic_lgas.json')
    melb_lgas = ["MELBOURNE", "PORT PHILLIP", "STONNINGTON", "YARRA", "BANYULE", "BAYSIDE", "BOROONDARA", "DAREBIN", "GLEN EIRA", "HOBSONS BAY", "KINGSTON", "MANNINGHAM", "MARIBYRNONG", "MONASH", "MOONEE VALLEY", "MORELAND", "WHITEHORSE", "BRIMBANK", "CARDINIA", "CASEY", "FRANKSTON", "GREATER DANDENONG", "HUME", "KNOX", "MAROONDAH", "MELTON", "MORNINGTON PENINSULA", "NILLUMBIK", "WHITTLESEA", "WYNDHAM", "YARRA RANGES"]
    # scale to greater Melbourne
    melb_gdfs = []
    for lga in melb_lgas:
        test = gdf[gdf.vic_lga__3 == lga]
        melb_gdfs.append(test)
    df = pd.concat(melb_gdfs)
    filtered_df = df[['vic_lga__3','geometry']]
    gdf = geopandas.GeoDataFrame(filtered_df)
    gdf.to_file("./static/greater_melb.geojson", driver="GeoJSON")
    
# input the geojson file name
def draw_env_choropleth(file_name="./static/greater_melb.geojson"):
    print("drawing env choro...")
    gdf = geopandas.read_file(file_name).explode(index_parts = True)

    env_sent = open('./static/env_sent.json')
    coords = json.load(env_sent)

    gdf['num_tweets'] = [0 for i in gdf.vic_lga__3]
    gdf['positive'] = [0 for i in gdf.vic_lga__3]
    gdf['negative'] = [0 for i in gdf.vic_lga__3]
    gdf['neutral'] = [0 for i in gdf.vic_lga__3]
    for i in coords['text']:
        point = geometry.Point(coords['coordinates'][i])
        count = 1
        # see if a point lays in a polygon
        poly = gdf.geometry.contains(point)
        gdf.num_tweets[poly] += count
        
        if coords['label'][i] == 'Positive':
            gdf.positive[poly] += count
        elif coords['label'][i] == 'Negative':
            gdf.negative[poly] += count
        elif coords['label'][i] == 'Neutral':
            gdf.neutral[poly] += count
            
    m = gdf.explore("num_tweets", cmap = "Dark2")
    outfp = "./templates/env_choropleth.html"
    m.save(outfp)

def draw_health_choropleth(file_name="./static/greater_melb.geojson"):
    print("drawing health choro...")
    gdf = geopandas.read_file(file_name).explode(index_parts = True)

    coords = get_coords('health_tweets_coordinates')

    gdf['num_tweets'] = [0 for i in gdf.vic_lga__3]
    for coord in coords:
        point = geometry.Point(coord['key'])
        # print(point)
        count = coord['value']

        # see if a point lays in a polygon
        poly = gdf.geometry.contains(point)
        gdf.num_tweets[poly] += count
    # print(gdf.num_tweets)
    
    m = gdf.explore("num_tweets", cmap = "Dark2")
    outfp = "./templates/health_choropleth.html"
    m.save(outfp)


def health_to_json(file_name="./static/greater_melb.geojson"):
    gdf = geopandas.read_file(file_name).explode(index_parts = True)

    env_sent = open('./static/health_sent.json')
    coords = json.load(env_sent)

    gdf['num_tweets'] = [0 for i in gdf.vic_lga__3]
    gdf['positive'] = [0 for i in gdf.vic_lga__3]
    gdf['negative'] = [0 for i in gdf.vic_lga__3]
    gdf['neutral'] = [0 for i in gdf.vic_lga__3]
    for i in coords['text']:
        point = geometry.Point(coords['coordinates'][i])
        count = 1
        # see if a point lays in a polygon
        poly = gdf.geometry.contains(point)
        gdf.num_tweets[poly] += count
        
        if coords['label'][i] == 'Positive':
            gdf.positive[poly] += count
        elif coords['label'][i] == 'Negative':
            gdf.negative[poly] += count
        elif coords['label'][i] == 'Neutral':
            gdf.neutral[poly] += count

    gdf.to_file("./static/health_num_tweets.json")


def env_to_json(file_name="./static/greater_melb.geojson"):
    gdf = geopandas.read_file(file_name).explode(index_parts = True)

    env_sent = open('./static/env_sent.json')
    coords = json.load(env_sent)

    gdf['num_tweets'] = [0 for i in gdf.vic_lga__3]
    gdf['positive'] = [0 for i in gdf.vic_lga__3]
    gdf['negative'] = [0 for i in gdf.vic_lga__3]
    gdf['neutral'] = [0 for i in gdf.vic_lga__3]
    for i in coords['text']:
        point = geometry.Point(coords['coordinates'][i])
        count = 1
        # see if a point lays in a polygon
        poly = gdf.geometry.contains(point)
        gdf.num_tweets[poly] += count
        
        if coords['label'][i] == 'Positive':
            gdf.positive[poly] += count
        elif coords['label'][i] == 'Negative':
            gdf.negative[poly] += count
        elif coords['label'][i] == 'Neutral':
            gdf.neutral[poly] += count

    gdf.to_file("./static/env_num_tweets.json")

# env_to_json()
# health_to_json()
# draw_health_choropleth()
# draw_env_choropleth()
