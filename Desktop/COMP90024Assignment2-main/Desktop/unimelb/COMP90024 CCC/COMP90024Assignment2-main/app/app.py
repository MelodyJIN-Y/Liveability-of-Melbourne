
from operator import concat
import requests
from flask import Flask, render_template, url_for, redirect
import json
from helper import *
# from sentimental_analysis import env_sentiment_analysis
import schedule
import time

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
    print(day_total_dict)
    # day_total_list = [{'key': key, 'value': day_total_dict[key]} for key in day_total_dict]
    day_labels = list(day_total_dict.keys())
    day_values = [day_total_dict[key] for key in day_labels]

    # call mapreduce function to retrieve number of tweets of each day in a week
    each_day_coord = get_data('environment_tweets_coordinates', '_design/weekday/_view/each_day?group_level=1')
    each_day_text = get_data('environment_tweets_text', '_design/weekday/_view/each_day?group_level=1')
    # merge lists
    each_day_total = concat_lists_of_dicts(each_day_text, each_day_coord)
    print(each_day_total)
    # order keys for chart drawing
    day_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    sorted_each_day = {}
    for key in day_order:
        if key in each_day_total.keys():
            sorted_each_day[key] = each_day_total[key]

    sorted_each_day_values = list(sorted_each_day.values())
    
    # retrieve coords for heatmap
    coords = get_coords('environment_tweets_coordinates')

    return render_template('environment.html', lang_json = json.dumps(lang_total_list), lang_labels = json.dumps(lang_labels), lang_values = json.dumps(lang_values),
    day_labels = json.dumps(day_labels), day_values = json.dumps(day_values), 
    each_day_labels = json.dumps(day_order), each_day_values = json.dumps(sorted_each_day_values)
    )

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
    print(each_day_total)
    # order keys for chart drawing
    day_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    sorted_each_day = {}
    for key in day_order:
        if key in each_day_total.keys():
            sorted_each_day[key] = each_day_total[key]

    sorted_each_day_values = list(sorted_each_day.values())
    
    # retrieve coords for heatmap
    coords = get_coords('environment_tweets_coordinates')

    return render_template('health.html', lang_json = json.dumps(lang_total_list), lang_labels = json.dumps(lang_labels), lang_values = json.dumps(lang_values),
    day_labels = json.dumps(day_labels), day_values = json.dumps(day_values), 
    each_day_labels = json.dumps(day_order), each_day_values = json.dumps(sorted_each_day_values)
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
    air_pollute_data = requests.get("http://admin:admin@172.26.132.125:5984/environment_aurin_pollute_emission/_all_docs?include_docs=true")
    air_pollute_data = json.loads(air_pollute_data.text)["rows"]
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
    weather_climate_data = requests.get("http://admin:admin@172.26.132.125:5984/environment_aurin_weather_climate/_all_docs?include_docs=true")
    weather_climate_data = json.loads(weather_climate_data.text)["rows"]
    return render_template('aurin_environment_weather_climate.html', weather_climate_json = weather_climate_data)

@app.route('/aurin_environment_waste')
def aurin_env_was():
    waste_recycling_data = requests.get("http://admin:admin@172.26.132.125:5984/environment_aurin_waste_recycling/_all_docs?include_docs=true")
    waste_recycling_data = json.loads( waste_recycling_data.text)["rows"]
    return render_template('aurin_environment_waste_recycling.html', waste_recycling_json = waste_recycling_data)

@app.route('/aurin_environment_air')
def aurin_env_air():
    air_monitoring_data = requests.get("http://admin:admin@172.26.132.125:5984/environment_aurin_air_monitoring/_all_docs?include_docs=true")
    air_monitoring_data = json.loads( air_monitoring_data.text)["rows"]
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
    cancer_ratio_data = requests.get("http://admin:admin@172.26.132.125:5984/health_aurin_cancer_betw_greats_data/_all_docs?include_docs=true")
    cancer_ratio_data = json.loads(cancer_ratio_data.text)["rows"]
    for i in range(len(cancer_ratio_data)):
        if cancer_ratio_data[i]["doc"]["lymphoma_c81_c86_rt_ratio"] is None:
            cancer_ratio_data[i]["doc"]["lymphoma_c81_c86_rt_ratio"] = 0
        if cancer_ratio_data[i]["doc"]["leukaemia_c91_c95_rt_ratio"] is None:
            cancer_ratio_data[i]["doc"]["leukaemia_c91_c95_rt_ratio"] = 0
    return render_template('aurin_health_cancer_rate.html', cancer_ratio_json = cancer_ratio_data)

@app.route('/aurin_health_essential')
def aurin_hea_ess():
    essential_data = requests.get("http://admin:admin@172.26.132.125:5984/health_aurin_essential_services_data/_all_docs?include_docs=true")
    essential_data = json.loads(essential_data.text)["rows"]
    return render_template('aurin_health_essential_services.html', essential_json=essential_data)

@app.route('/aurin_health_hospital')
def aurin_hea_hos():
    gp_hospital_data = requests.get("http://admin:admin@172.26.132.125:5984/health_aurin_gp_data/_all_docs?include_docs=true")
    gp_hospital_data = json.loads(gp_hospital_data.text)["rows"]
    return render_template('aurin_health_hospital_gp.html', gp_hospital_json=gp_hospital_data)

@app.route('/aurin_health_age')
def aurin_hea_age():
    median_age_data = requests.get("http://admin:admin@172.26.132.125:5984/health_aurin_median_age_data/_all_docs?include_docs=true")
    median_age_data = json.loads(median_age_data.text)["rows"]
    return render_template('aurin_health_median_age.html', median_age_json = median_age_data)

@app.route('/env_rel1')
def scenario1():
    weather_climate_data = requests.get("http://admin:admin@172.26.132.125:5984/environment_aurin_weather_climate/_all_docs?include_docs=true")
    weather_climate_data = json.loads(weather_climate_data.text)["rows"]
    return render_template('env_rel.html', weather_climate_json = weather_climate_data)

@app.route('/env_rel2')
def scenario2():
    weather_climate_data = requests.get("http://admin:admin@172.26.132.125:5984/environment_aurin_weather_climate/_all_docs?include_docs=true")
    weather_climate_data = json.loads(weather_climate_data.text)["rows"]
    return render_template('negative.html', weather_climate_json = weather_climate_data)

@app.route('/env_rel3')
def scenario3():
    essential_data = requests.get("http://admin:admin@172.26.132.125:5984/health_aurin_essential_services_data/_all_docs?include_docs=true")
    essential_data = json.loads(essential_data.text)["rows"]
    return render_template('health_positive.html', essential_json=essential_data)

@app.route('/env_rel4')
def scenario4():
    return render_template('health_negative.html')

if __name__ == "__main__":
    
    app.run(debug=True)
    
    
