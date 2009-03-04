#!/usr/bin/env python
#coding=utf-8

""" zelfratz is a tool to track artist and lable releases on digital-tunes """

import pycurl, xml.dom.minidom, StringIO, optparse

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
        print "release: ", self.name.encode()
        print "by: ", [a.encode() for a in self.artists]
        print "on label: ", self.label.encode()
        print "url: ", self.url.encode()

class track():
    """ holds really basic information about a track """
    def __init__(self, name,url):
        self.name = name
        self.url = url
    def pretty_print(self):
        print "track: ", self.name.encode()
        print "url: ", self.url.encode()

def __init__():
    """ perform initialisation of libcurl and read api key from file """
    global curl
    curl = pycurl.Curl()
    global key
    key = read_key_from_file('api-key')

def create_api_request(type,search):
    """ create a digital-tunes api request as a string """
    url = 'http://api.digital-tunes.net/'
    if type == ARTIST:
        url += "tracks/by_artist/"
    elif type == LABEL:
        url += "releases/by_label/"
    else:
        print "create_api_request invoked with incorrect argument:" + TYPE
        sys.exit()
    url += search + "?key=" + key
    return url

def parse_release_xml(release_xml):
    """ parse xml returned by a 'release' query into list of release obkects """
    x = xml.dom.minidom.parseString(release_xml)
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

def parse_track_xml(track_xml):
    """ parse xml returned by a 'track' query into a list of track objects """
    x = xml.dom.minidom.parseString(track_xml)
    tracks = list()
    for tra in x.getElementsByTagName('track'):
        name = tra.getElementsByTagName('name')[0].firstChild.data
        rel = tra.getElementsByTagName('release')[0]
        u= rel.getElementsByTagName('url')[0].firstChild.data
        tracks.append(track(name,u))
    return tracks

    
def read_key_from_file(filename):
    """ read the application specific key from a file """
    file = open(filename)
    key = file.readline()
    key = key.rstrip()
    file.close()
    return key

def do_api_call(url):
    """ do the api call to digital-tunes and return the xml """
    curl.setopt(pycurl.URL, url)
    b = StringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, b.write)
    curl.perform()
    return b.getvalue()

if __name__ ==  "__main__":
    __init__()
    url = create_api_request(ARTIST,"pyro")
    x = do_api_call(url)
    print x
    li = parse_track_xml(x)
    for l in li:
        l.pretty_print()

