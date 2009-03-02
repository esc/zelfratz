#!/usr/bin/env python
#coding=utf-8

""" zelfratz is tool to track artist and lable relaeses on digital-tunes """

import pycurl
ARTIST = 1
LABEL = 2
artists = ['pyro']
key = "666"
curl = None

def __init__():
    """ perform initialisation of libcurl """
    curl = pycurl.Curl()
    global key
    key = read_key_from_file()

def create_api_request(type,search):
    """ create a digital-tunes api request as a string """
    url = 'http://api.digital-tunes.net/releases/'
    if type == ARTIST:
        url += "by_artist/"
    elif type == LABEL:
        url += "by_label/"
    #elif THROW MAYOR PRGOGRAMMER TYPE ERROR
    url += search
    url += "?key="
    url += key
    return url
    
def read_key_from_file():
    """ read the application specific key from a file """
    file = open('api-key')
    key = file.readline()
    key = key.rstrip()
    file.close()
    return key

def do_api_call(url):
    """ do the api call to digital-tunes and return the xml """
    curl.setopt(pycurl.URL, url)
    return curl.perform()

if __name__ ==  "__main__":
    __init__()
    print create_api_request(ARTIST,'pyro')
