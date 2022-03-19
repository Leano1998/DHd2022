import pandas as pd
import requests
import json
import datetime
import pytz

def header_authorization(ini_file: str) -> dict:
    """
    Function returns the header including the bearer-token of the access
    informations in the ini_file to connect with the api.

    :param ini_file: The path to the ini-file.
    :return: The bearer token
    """
    access_info = {}
    with open(ini_file) as f:
        for l in f.readlines():
            tmp = l.split(': ')
            access_info[tmp[0]] = tmp[1].strip('\n')

    return {"Authorization": "Bearer {}".format(access_info["bearer_token"])}


def create_url_params(query: str, start_date: str=None, end_date: str=None,
                        max_results:int = 100) -> tuple:
    """
    Creating URL and parameters for the connection to the Twitter_API.

    :param query: The query containing the keywords for the search.
    :param start_date: The startdate of the search in ISO-Format: YYYY:MM:DDTHH:MM:SSZ
    :param end_date: The enddate of the search in ISO-Format.
    :param max_results: The maximum results of the search.
    :return: Returns the URL and the parameters as a tuple (url, parameters)
    """
    if start_date is None and end_date is None:
        # Creating the dateinformation based on the current time minus one week.
        end_date = datetime.datetime.now(pytz.utc)-datetime.timedelta(seconds=10)
        start_date = str(end_date - datetime.timedelta(days=6,
                                                        hours=23,
                                                        minutes=59)
                        ).replace(' ', 'T')[:-7] + 'Z'
        end_date = str(end_date).replace(' ', 'T')[:-7] + 'Z'
    url = "https://api.twitter.com/2/tweets/search/recent"
    #change params based on the endpoint you are using
    query_params = {'query': query,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'text,author_id,created_at,entities,in_reply_to_user_id,lang,public_metrics,source,geo',
                    'user.fields': 'id,name,username,created_at,description,entities,public_metrics,verified',
                    'place.fields': 'full_name,country,geo',
                    'next_token': {}}
    return (url, query_params)

def connect_to_api(url: str, headers: dict, params: dict, next_token: str = None):
    """
    The connection to the Twitter API based on the given parameters.

    :param url: The url of the Twitter-API endpoint.
    :param headers: The header information for the connection containing the bearer-token.
    :param params: The parameters for the search as a dictonary.
    :param next_token: The next_token only given if there are unseen results from the last search.
    :return: Returns the response in JSON format.
    """
    params['next_token'] = next_token
    try:
        response = requests.request("GET", url, headers = headers, params = params)
    except requests.exceptions.ConnectionError:
        print("No internet connection possible!")
        return None
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def search_tweets(query: str, next_token:str = None, max_results: int=100):
    """
    Search tweets by connecting to the Twitter-API while using the existing
    functions.

    :param query: The query containing the keywords for the search.
    :param next_token: The next_token only given if there are unseen results from the last search.
    :return: The API-response to the search as JSON-format.
    """
    url, params = create_url_params(query, max_results=max_results)
    return connect_to_api(url, header_authorization('twitter_api.ini'), params, next_token)
