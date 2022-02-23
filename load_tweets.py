import tweepy
import pandas as pd


def connect_api(ini_file: str):
    """
    Function returns an open API-connection with the access informations in the ini_file.

    :param ini_file: the path to the ini-file.
    :return: The working api-connection.
    """
    access_info = {}
    with open(ini_file) as f:
        for l in f.readlines():
            tmp = l.split(': ')
            access_info[tmp[0]] = tmp[1].strip('\n')
    auth = tweepy.OAuthHandler(access_info['api_key'], access_info['api_secret'])
    auth.set_access_token(access_info['access_token'], access_info['access_secret'])
    return access_info
