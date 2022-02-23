import tweepy
import pandas as pd
import requests
import json
import datetime
import pytz

def connect_api(ini_file: str) -> str:
    """
    Function returns the bearer-token of the access informations in the ini_file.

    :param ini_file: the path to the ini-file.
    :return: The bearer token
    """
    access_info = {}
    with open(ini_file) as f:
        for l in f.readlines():
            tmp = l.split(': ')
            access_info[tmp[0]] = tmp[1].strip('\n')
    #client = tweepy.Client(consumer_key = access_info['api_key'], consumer_secret = access_info['api_secret'],
    #                        access_token = access_info['access_token'], access_token_secret = access_info['access_secret'])


    return access_info["bearer_token"]


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, start_date=None, end_date=None, max_results = 100):
    if start_date is None and end_date is None:
        end_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(seconds=10)
        start_date = str(end_date - datetime.timedelta(days=6, hours=23, minutes=59)).replace(' ', 'T')[:-7] + 'Z'
        end_date = str(end_date).replace(' ', 'T')[:-7] + 'Z'
    search_url = "https://api.twitter.com/2/tweets/search/recent" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'text,author_id,created_at,entities,in_reply_to_user_id,lang,public_metrics,source,geo',
                    'user.fields': 'id,name,username,created_at,description,entities,public_metrics,verified',
                    'place.fields': 'full_name,country,geo',
                    'next_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def search_tweets(query: str, next_token = None):
    url, params = create_url(query)
    return connect_to_endpoint(url, create_headers(connect_api('twitter_api.ini')), params, next_token)
