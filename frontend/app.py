
import requests
from flask import Flask, render_template, url_for, redirect
import json
from helper import *
import time
import base64
import pandas as pd
from datetime import date

app = Flask(__name__)

# main page route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/envrionment_heatmap')
def env_map():
    coords = get_coords('environment_tweets_coordinates')
    return render_template('env_map.html', coords = json.dumps(coords))

@app.route('/environment_choropleth')
def env_choro():
    return render_template('env_choropleth.html')

# language page route
@app.route('/environment')
def env():
     # send http request to couchdb that calls mapreduce
    lang_list_text = get_data("environment_tweets_text", "_design/lang/_view/lang?group_level=1")
    lang_list_coord = get_data("environment_tweets_coordinates", "_design/lang/_view/lang?group_level=1")

    # merge two lists
    lang_total_dict = concat_lists_of_dicts(lang_list_text, lang_list_coord)
    lang_total_list = [{'key': key, 'value': lang_total_dict[key]} for key in lang_total_dict]

    lang_labels = [lang_dict['key'] for lang_dict in lang_total_list]
    lang_values = [lang_dict['value'] for lang_dict in lang_total_list]
    
    # get day data
    day_list_coord = get_data("environment_tweets_coordinates", "_design/weekday/_view/weekday_or_weekend?group_level=1")
    day_list_text = get_data("environment_tweets_text", "_design/weekday/_view/weekday_or_weekend?group_level=1")

    day_total_dict = concat_lists_of_dicts(day_list_text, day_list_coord)
    # print(day_total_dict)
    # day_total_list = [{'key': key, 'value': day_total_dict[key]} for key in day_total_dict]
    day_labels = list(day_total_dict.keys())
    day_values = [day_total_dict[key] for key in day_labels]

    # call mapreduce function to retrieve number of tweets of each day in a week
    each_day_coord = get_data('environment_tweets_coordinates', '_design/weekday/_view/each_day?group_level=1')
    each_day_text = get_data('environment_tweets_text', '_design/weekday/_view/each_day?group_level=1')
    # merge lists
    each_day_total = concat_lists_of_dicts(each_day_text, each_day_coord)
    # print(each_day_total)
    # order keys for chart drawing
    day_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    sorted_each_day = {}
    for key in day_order:
        if key in each_day_total.keys():
            sorted_each_day[key] = each_day_total[key]

    sorted_each_day_values = list(sorted_each_day.values())

    # get word cloud
    # add username and password
    couch = couchdb.Server('http://172.26.132.125:5984/')
    couch.resource.credentials = ("admin", "admin")
    # find the latest id   
    ids = get_data('environment_tweets_text_wordcloud', '_design/get_id/_view/view')

    max_time = ids[0]["id"]
    for img_id in ids:
        if img_id["id"] > max_time:
            max_time = img_id['id']

    db = couch['environment_tweets_text_wordcloud']
    doc = db.get_attachment(max_time, 'wc_fig.png').read()

    img_b64 = base64.b64encode(doc).decode("utf-8")

    # get sentimental data for line chart

    pos_data = get_data('environment_tweets_text_sentiment', '_design/label_date/_view/positive?group_level=1')
    pos = []
    for i in pos_data:
        if i['key'] >= '2022-01-01':
            pos.append(i)

    neg_data = get_data('environment_tweets_text_sentiment', '_design/label_date/_view/negative?group_level=1')
    neg = []

    for i in neg_data:
        if i['key'] >= '2022-01-01':
            neg.append(i)

    neu_data = get_data('environment_tweets_text_sentiment', '_design/label_date/_view/neutral?group_level=1')
    neu = []

    for i in neu_data:
        if i['key'] >= '2022-01-01':
            neu.append(i)
    today = date.today()
    date_range = pd.date_range('2022-01-01', today).tolist()
    simple_date = []
    for day in date_range:
        simple_date.append(day.strftime("%Y-%m-%d"))
    # print(simple_date)


    return render_template('environment.html', lang_json = json.dumps(lang_total_list), lang_labels = json.dumps(lang_labels), lang_values = json.dumps(lang_values),
    day_labels = json.dumps(day_labels), day_values = json.dumps(day_values), 
    each_day_labels = json.dumps(day_order), each_day_values = json.dumps(sorted_each_day_values),
    img_b64 = img_b64, pos_data = json.dumps(pos), neg_data = json.dumps(neg), neu_data = json.dumps(neu), date_range = simple_date)

# health charts
@app.route('/health')
def health():
    # send http request to couchdb that calls mapreduce
    lang_list_text = get_data("health_tweets_text", "_design/lang/_view/lang?group_level=1")
    lang_list_coord = get_data("health_tweets_coordinates", "_design/lang/_view/lang?group_level=1")

    # merge two lists
    lang_total_dict = concat_lists_of_dicts(lang_list_text, lang_list_coord)


    lang_total_list = [{'key': key, 'value': lang_total_dict[key]} for key in lang_total_dict]

    lang_labels = [lang_dict['key'] for lang_dict in lang_total_list]
    lang_values = [lang_dict['value'] for lang_dict in lang_total_list]
    
    # get day data
    day_list_coord = get_data("health_tweets_coordinates","_design/weekday/_view/weekday_or_weekend?group_level=1")
    day_list_text = get_data("health_tweets_text", "_design/weekday/_view/weekday_or_weekend?group_level=1")

    day_total_dict = concat_lists_of_dicts(day_list_text, day_list_coord)
    day_labels = list(day_total_dict.keys())
    day_values = [day_total_dict[key] for key in day_labels]

    # call mapreduce function to retrieve number of tweets of each day in a week
    each_day_coord = get_data("health_tweets_coordinates", "_design/weekday/_view/each_day?group_level=1")
    each_day_text = get_data("health_tweets_text", "_design/weekday/_view/each_day?group_level=1")

    each_day_total = concat_lists_of_dicts(each_day_text, each_day_coord)
    # print(each_day_total)
    # order keys for chart drawing
    day_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    sorted_each_day = {}
    for key in day_order:
        if key in each_day_total.keys():
            sorted_each_day[key] = each_day_total[key]

    sorted_each_day_values = list(sorted_each_day.values())

    # get word cloud
    # add username and password
    couch = couchdb.Server('http://172.26.132.125:5984/')
    couch.resource.credentials = ("admin", "admin")
    # find the latest id   
    ids = get_data('health_tweets_text_wordcloud', '_design/get_id/_view/view')

    max_time = ids[0]["id"]
    for img_id in ids:
        if img_id["id"] > max_time:
            max_time = img_id['id']

    db = couch['health_tweets_text_wordcloud']
    doc = db.get_attachment(max_time, 'wc_fig.png').read()

    img_b64 = base64.b64encode(doc).decode("utf-8")

    # get sentimental data for line chart

    pos_data = get_data('health_tweets_text_sentiment', '_design/label_date/_view/positive?group_level=1')
    pos = []
    for i in pos_data:
        if i['key'] >= '2022-01-01':
            pos.append(i)

    neg_data = get_data('health_tweets_text_sentiment', '_design/label_date/_view/negative?group_level=1')
    neg = []

    for i in neg_data:
        if i['key'] >= '2022-01-01':
            neg.append(i)

    neu_data = get_data('health_tweets_text_sentiment', '_design/label_date/_view/neutral?group_level=1')
    neu = []

    for i in neu_data:
        if i['key'] >= '2022-01-01':
            neu.append(i)
    today = date.today()
    date_range = pd.date_range('2022-01-01', today).tolist()
    simple_date = []
    for day in date_range:
        simple_date.append(day.strftime("%Y-%m-%d"))

    return render_template('health.html', lang_json = json.dumps(lang_total_list), lang_labels = json.dumps(lang_labels), lang_values = json.dumps(lang_values),
    day_labels = json.dumps(day_labels), day_values = json.dumps(day_values), 
    each_day_labels = json.dumps(day_order), each_day_values = json.dumps(sorted_each_day_values),
    img_b64 = img_b64, pos_data = json.dumps(pos), neg_data = json.dumps(neg), neu_data = json.dumps(neu), date_range = simple_date
    )

# health heatmap
@app.route('/health_heatmap')
def health_map():
    coords = get_coords('health_tweets_coordinates')
    return render_template('health_map.html', coords = json.dumps(coords))

# health choropleth
@app.route('/health_choropleth')
def health_choro():
    return render_template('health_choropleth.html')

@app.route('/aurin_environment_pollute')
def aurin_env_pol():
    air_pollute_data = get_data("environment_aurin_pollute_emission", "_all_docs?include_docs=true")
    # air_pollute_data = json.loads(air_pollute_data.text)["rows"]
    for i in range(len(air_pollute_data)):
        if air_pollute_data[i]["doc"]["air_fugitive_eet"] is None:
            air_pollute_data[i]["doc"]["air_fugitive_eet"] = "null"
        if air_pollute_data[i]["doc"]["air_fugitive_emission_kg"] is None:
            air_pollute_data[i]["doc"]["air_fugitive_emission_kg"] = "null"
        if air_pollute_data[i]["doc"]["water_emission_kg"] is None:
            air_pollute_data[i]["doc"]["water_emission_kg"] = "null"
        if air_pollute_data[i]["doc"]["land_emission_kg"] is None:
            air_pollute_data[i]["doc"]["land_emission_kg"] = "null"
        if air_pollute_data[i]["doc"]["land_eet"] is None:
            air_pollute_data[i]["doc"]["land_eet"] = "null"
        if air_pollute_data[i]["doc"]["water_eet"] is None:
            air_pollute_data[i]["doc"]["water_eet"] = "null"
    return render_template('aurin_environment_pollute_emission.html', air_pollute_json = air_pollute_data)

@app.route('/aurin_environment_weather')
def aurin_env_wea():
    weather_climate_data = get_data("environment_aurin_weather_climate", "_all_docs?include_docs=true")
    # weather_climate_data = json.loads(weather_climate_data.text)["rows"]
    return render_template('aurin_environment_weather_climate.html', weather_climate_json = weather_climate_data)

@app.route('/aurin_environment_waste')
def aurin_env_was():
    waste_recycling_data = get_data("environment_aurin_waste_recycling", "_all_docs?include_docs=true")
    # waste_recycling_data = json.loads( waste_recycling_data.text)["rows"]
    return render_template('aurin_environment_waste_recycling.html', waste_recycling_json = waste_recycling_data)

@app.route('/aurin_environment_air')
def aurin_env_air():
    air_monitoring_data = get_data("environment_aurin_air_monitoring", "_all_docs?include_docs=true")
    # air_monitoring_data = json.loads( air_monitoring_data.text)["rows"]
    for i in range(len(air_monitoring_data)):
        if air_monitoring_data[i]["doc"]["sites_hasincident"] is True:
            air_monitoring_data[i]["doc"]["sites_hasincident"] = "true"
        if air_monitoring_data[i]["doc"]["sites_hasincident"] is False:
            air_monitoring_data[i]["doc"]["sites_hasincident"] = "false"
        if air_monitoring_data[i]["doc"]["sites_isstationoffline"] is False:
            air_monitoring_data[i]["doc"]["sites_isstationoffline"] = "false"
    return render_template('aurin_environment_air_monitoring.html', air_monitoring_json = air_monitoring_data)

@app.route('/aurin_health_cancer')
def aurin_hea_can():
    cancer_ratio_data = get_data("health_aurin_cancer_betw_greats_data", "_all_docs?include_docs=true")
    # cancer_ratio_data = json.loads(cancer_ratio_data.text)["rows"]
    for i in range(len(cancer_ratio_data)):
        if cancer_ratio_data[i]["doc"]["lymphoma_c81_c86_rt_ratio"] is None:
            cancer_ratio_data[i]["doc"]["lymphoma_c81_c86_rt_ratio"] = 0
        if cancer_ratio_data[i]["doc"]["leukaemia_c91_c95_rt_ratio"] is None:
            cancer_ratio_data[i]["doc"]["leukaemia_c91_c95_rt_ratio"] = 0
    return render_template('aurin_health_cancer_rate.html', cancer_ratio_json = cancer_ratio_data)

@app.route('/aurin_health_essential')
def aurin_hea_ess():
    essential_data = get_data("health_aurin_essential_services_data", "_all_docs?include_docs=true")
    # essential_data = json.loads(essential_data.text)["rows"]
    return render_template('aurin_health_essential_services.html', essential_json=essential_data)

@app.route('/aurin_health_hospital')
def aurin_hea_hos():
    gp_hospital_data = get_data("health_aurin_gp_data", "_all_docs?include_docs=true")
    # gp_hospital_data = json.loads(gp_hospital_data.text)["rows"]
    return render_template('aurin_health_hospital_gp.html', gp_hospital_json=gp_hospital_data)

@app.route('/aurin_health_age')
def aurin_hea_age():
    median_age_data = get_data("health_aurin_median_age_data", "_all_docs?include_docs=true")
    # median_age_data = json.loads(median_age_data.text)["rows"]
    return render_template('aurin_health_median_age.html', median_age_json = median_age_data)

@app.route('/env_rel1')
def scenario1():
    weather_climate_data = get_data("environment_aurin_weather_climate", "_all_docs?include_docs=true")
    pos_data = get_data('environment_tweets_text_sentiment', '_design/label_date/_view/positive?group_level=1')
    pos = []
    # print(pos_data)
    for i in pos_data:
        if (i['key'] >= '2022-03-08' and i['key'] <= '2022-04-30'):
            pos.append(i)
    # print(pos)
    
    return render_template('env_rel.html', weather_climate_json = weather_climate_data, pos_data = pos)

@app.route('/env_rel2')
def scenario2():
    weather_climate_data = get_data("environment_aurin_weather_climate", "_all_docs?include_docs=true")
    neg_data = get_data('environment_tweets_text_sentiment', '_design/label_date/_view/negative?group_level=1')
    neg = []
    for i in neg_data:
        if (i['key'] >= '2022-01-01' and i['key'] <= '2022-04-01'):
            neg.append(i)

    return render_template('negative.html', weather_climate_json = weather_climate_data, neg_data = neg)

@app.route('/env_rel3')
def scenario3():
    essential_data = get_data("health_aurin_essential_services_data", "_all_docs?include_docs=true")
    # essential_data = json.loads(essential_data.text)["rows"]
    return render_template('health_positive.html', essential_json=essential_data)

@app.route('/env_rel4')
def scenario4():
    gp_hospital_data = get_data("health_aurin_gp_data", "_all_docs?include_docs=true")
    return render_template('health_negative.html', gp_hospital_json=gp_hospital_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

