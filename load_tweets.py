import requests
import datetime
import pytz
import pandas as pd


def header_authorization(ini_file: str) -> dict:
    """
    Function returns the header including the bearer-token of the access
    information in the ini_file to connect with the api.

    :param ini_file: The path to the ini-file.
    :return: The bearer token
    """
    access_info = {}
    with open(ini_file) as f:
        for line in f.readlines():
            tmp = line.split(': ')
            access_info[tmp[0]] = tmp[1].strip('\n')

    return {"Authorization": "Bearer {}".format(access_info["bearer_token"])}


def create_url_params(query: str, start_date: str = None, end_date: str = None, max_results: int = 100) -> tuple:
    """
    Creating URL and parameters for the connection to the Twitter_API.

    :param query: The query containing the keywords for the search.
    :param start_date: The start-date of the search in ISO-Format: "YYYY:MM:DDTHH:MM:SSZ"
    :param end_date: The end-date of the search in ISO-Format.
    :param max_results: The maximum results of the search.
    :return: Returns the URL and the parameters as a tuple (url, parameters)
    """
    if start_date is None and end_date is None:
        # Creating the date-information based on the current time minus one week.
        end_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(seconds=10)
        start_date = str(end_date - datetime.timedelta(days=6,
                                                       hours=23,
                                                       minutes=59)
                         ).replace(' ', 'T')[:-7] + 'Z'
        end_date = str(end_date).replace(' ', 'T')[:-7] + 'Z'
    url = "https://api.twitter.com/2/tweets/search/recent"

    query_params = {
        'query': query,
        'start_time': start_date,
        'end_time': end_date,
        'max_results': max_results,
        'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
        'tweet.fields': 'text,author_id,created_at,entities,in_reply_to_user_id,lang,public_metrics,source,geo',
        'user.fields': 'id,name,username,created_at,description,entities,public_metrics,verified',
        'place.fields': 'full_name,country,geo',
        'next_token': {}
    }
    return url, query_params


def connect_to_api(url: str, headers: dict, params: dict, next_token: str = None):
    """
    The connection to the Twitter API based on the given parameters.

    :param url: The url of the Twitter-API endpoint.
    :param headers: The header information for the connection containing the bearer-token.
    :param params: The parameters for the search as a dictionary.
    :param next_token: The next_token only given if there are unseen results from the last search.
    :return: Returns the response in JSON format.
    """
    params['next_token'] = next_token
    try:
        response = requests.request("GET", url, headers=headers, params=params)
    except requests.exceptions.ConnectionError:
        print("No internet connection possible!")
        return None
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def search_tweets(query: str, next_token: str = None, max_results: int = 100):
    """
    Search tweets by connecting to the Twitter-API while using the existing
    functions.

    :param query: The query containing the keywords for the search.
    :param next_token: The next_token only given if there are unseen results from the last search.
    :param max_results: The maximum number of results.
    :return: The API-response to the search as JSON-format.
    """
    url, params = create_url_params(query, max_results=max_results)
    return connect_to_api(url, header_authorization('twitter_api.ini'), params, next_token)


def convert_datetime(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    A function to convert the column of a dataframe containing ISO-Format ("YYYY-MM-DDTHH:MM:SSZ") values for time
    information into datetime objects.

    :param df: The dataframe.
    :param column: The column of the given dataframe containing the time information.
    :return: The dataframe with the new formatted values.
    """
    def iso_to_datetime(iso: str) -> datetime.datetime:
        iso = iso.split('T')
        date, day_time = iso[0].split('-'), iso[1].strip('Z').split(':')
        try:
            return datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(day_time[0]), int(day_time[1]),
                                     int(float(day_time[2])))
        except ValueError:
            raise ValueError('The string isn\'t iso-formatted. Expected: YYYY-MM-DDTHH:MM:SSZ, but got: %s' % iso)

    df = pd.DataFrame(df)
    time_col = []
    for _, v in df.iterrows():
        if not pd.isna(v[column]):
            time_col.append(iso_to_datetime(v[column]))
        else:
            time_col.append(None)
    df[column] = pd.Series(time_col)
    return df
