#!/usr/bin/env python
#coding=utf-8

""" zelfratz is a tool to track artist and lable relaeses on digital-tunes """

import pycurl
import xml.dom.minidom

ARTIST = 1
LABEL = 2
key = "666"
curl = None

class release():
    """ holds really basic information about a release """
    def __init__(self, name, artists,label,url):
        self.name = name
        self.artists = artists
        self.label = label
        self.url = url
    def pretty_print(self):
        print self.name.encode()
        print "by: ", [a.encode() for a in self.artists]
        print "on label: ", self.label.encode()
        print "url: ", self.url.encode()

def __init__():
    """ perform initialisation of libcurl and read api key from file """
    global curl
    curl = pycurl.Curl()
    global key
    key = read_key_from_file()

def create_api_request(type,search):
    """ create a digital-tunes api request as a string """
    url = 'http://api.digital-tunes.net/releases'
    if type == ARTIST:
        url += "by_artist/"
    elif type == LABEL:
        url += "by_label/"
    #elif THROW MAYOR PRGOGRAMMER TYPE ERROR
    url += search
    url += "?key="
    url += key
    return url

def parse_artist_xml(release_xml):
    """ parse xml returned by a 'release' query into list of release obkects """
    x = xml.dom.minidom.parseString(artist_xml)
    releases = list()
    for rel in x.getElementsByTagName('release'):
        name = rel.getElementsByTagName('name')[0].firstChild.data
        url = rel.getElementsByTagName('url')[0].firstChild.data
        tmp = rel.getElementsByTagName('artists')[0]
        artists = []
        for art in tmp.getElementsByTagName('artist'):
            artists.append(art.firstChild.data)
        tmp = rel.getElementsByTagName('label')[0]
        tmp = tmp.getElementsByTagName('name')[0]
        label = tmp.firstChild.data
        releases.append(release(name,artists,label,url))
    return releases
    
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
    x = open('artists.xml').read()
    li = parse_artist_xml(x)
    for l in li:
        l.pretty_print()

