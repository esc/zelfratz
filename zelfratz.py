#!/usr/bin/env python
#coding=utf-8

# "zelfratz" is (!C) 2009 Valentin 'esc' Haenel
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.


""" zelfratz is a tool to track artist and label releases on digital-tunes """

import pycurl, xml.dom.minidom, StringIO, optparse, os, pickle, urllib2, sys, \
inspect

VERSION = 0.2
AUTHOR = 'esc'
ARTIST = 0
LABEL = 1
curl = pycurl.Curl()
conf = None

def etype_check(func):
    """ decorator to check that the correct etype encoding is passed """
    def decorate(*arg, **kwargs):
        arg_names = inspect.getargspec(func)[0]
        if 'etype' in arg_names:
            id = arg_names.index('etype')
            if arg[id] not in (ARTIST,LABEL):
                err_str = "create_api_request invoked with incorrect argument:" \
                + str(arg[id]) + "\nUse zelfratz.ARTIST or zelfratz.LABEL instead of raw " + \
                "integers."
                raise(TypeError(err_str))
        res = func(*arg , **kwargs)
        return res
    return decorate

class configuration():
    """ holds zelfratz config """
    def __init__(self, cache_file, cache, key, debug=False):
        self.cache_file = cache_file
        self.cache = cache
        self.key = key
        self.debug = debug

class release():
    """ holds really basic information about a release """
    def __init__(self, name, artists, label, url):
        self.name = name
        self.artists = artists
        self.label = label
        self.url = url
        self.hash = 0
        self.values = (self.name, self.artists, self.label, self.url)

    def pretty_print(self):
        print "release: ", self.name.encode('ascii','ignore')
        print "by: ", [a.encode('ascii','ignore') for a in self.artists]
        print "on label: ", self.label.encode('ascii','ignore')
        print "url: ", self.url.encode('ascii','ignore')

    def __cmp__(self, other):
        return cmp(self.values, other.values)

    def __hash__(self):
        if self.hash == 0:
            result = 23
            for v in self.values:
                if type(v) == str:
                    result = 37 * result + v.__hash__()
            self.hash = result
        return self.hash

class zdata():
    """ holds all user data for zelfratz

        This class holds all known artists and labels, and their respective
        releases. This class is what is serialised and stored to disk as cache.

        The information is stored in two dictionaries, one for artists, one for
        labels, where the keys are the names of the entities(artists or labels),
        and the values are sets, that contain release instances.

    """
    def __init__(self):
        self.artists = dict()
        self.labels = dict()
        self.entities = [self.artists, self.labels]

    def contains_artist(self, artist):
        return self.artists.has_key(artist)

    def contains_label(self, label):
        return self.labels.has_key(label)

    def update_artist(self, artist, releases):
        """ wrapper for update """
        self.update(ARTIST, artist, releases)

    def update_label(self, label, releases):
        """ wrapper for update """
        self.update(LABEL, label, releases)

    @etype_check
    def update(self, etype, entity, releases):
        """ if entity exists, append releases, else add entity and releases

            arguments:
            etype        - entity type constant
            entity      - string describing the entity
            releases    - a set of release instances

        """
        if self.entities[etype].has_key(entity):
            rel_set = self.entities[etype][entity]
            for r in releases:
                rel_set.add(r)
        else:
            self.entities[etype][entity] = releases

    def pretty_print(self):
        print_entity_releases(ARTIST, self.artists)
        print_entity_releases(LABEL, self.labels)

    def __cmp__(self, other):
        return cmp(self.entities, other.entities)

@etype_check
def print_entity_releases(etype, entity_releases):
    """ pretty print a dictionary that maps strings to sets of releases """
    if etype == ARTIST:
        descriptor = "by artist: "
    elif etype == LABEL:
        descriptor = "on label:"
    for i in entity_releases.keys():
        print '####################'
        print "releases" , descriptor, i
        for r in entity_releases[i]:
            r.pretty_print()

def print_debug(message):
    if conf.debug == True:
        print message

@etype_check
def create_api_request(etype, search):
    """ create a digital-tunes api request as a string """
    url = 'http://api.digital-tunes.net/releases/'
    if etype == ARTIST:
        url += "by_artist/"
    elif etype == LABEL:
        url += "by_label/"
    url += urllib2.quote(search) + "?key=" + conf.key
    return url

def do_api_call(url):
    """ do the api call to digital-tunes and return the xml """
    curl.setopt(pycurl.URL, url)
    b = StringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, b.write)
    curl.perform()
    return b.getvalue()

def parse_release_xml(release_xml):
    """ parse xml returned by a 'release' query into list of release instances """
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
        releases.append(release(name, artists, label, url))
    return releases

def get_artist_releases(artist):
    """ wrapper for get_entity_releases"""
    return get_entity_releases(ARTIST, artist)

def get_label_releases(label):
    """ wrapper for get_entity_releases"""
    return get_entity_releases(LABEL, label)

@etype_check
def get_entity_releases(etype, entity):
    """ wrapper: create api request, execute, and parse resulting xml """
    print_debug("searching for: " + entity)
    ur = create_api_request(etype, entity)
    print_debug("api string is: " + ur)
    xm = do_api_call(ur)
    return set(parse_release_xml(xm))

def read_key_from_file(filename):
    """ read the application specific key from a file """
    file = open(filename, 'r')
    key = file.readline().rstrip()
    file.close()
    return key

def read_list_from_file(filename):
    """ read the list strings from a file """
    file = open(filename, 'r')
    l = [s.rstrip() for s in file.readlines()]
    file.close()
    return l

def read_cache(filename):
    """ read zdata instance from filesystem, if file doesn't exist, return new"""
    if not os.path.isfile(filename):
        return zdata()
    else:
        file = open(filename, 'r')
        zd = pickle.loads(pickle.load(file))
        file.close()
        return zd

def write_cache(zd, filename):
    """ write zdata instance to filesystem """
    file = open(filename, 'w')
    pickle.dump(pickle.dumps(zd), file)
    file.flush()
    file.close()

def check_updates_artists(artists):
    """ wrapper for check_updates """
    return check_updates(ARTIST, artists)

def check_updates_labels(labels):
    """ wrapper for check_updates """
    return check_updates(LABEL, labels)

@etype_check
def check_updates(etype, entities):
    """ check for new releases

        This function will do the following: for each entity in a list of
        entities, connect to digital-tunes and get a list of releases. Then
        compare this list to whats in the local cache. If there are new releases
        for this entity add them to the cache, and return them. If this entity
        wasn't in the cache at all, add all releases to the cache and return. If
        all the releases are known return nothing for this entity.

        arguments:
        etype        - entity type constant
        entities    - a list of entities

        returns:
        a dictionary mapping names of entities to sets of release instances,

    """
    new_releases = dict()
    for e in entities:
        new = get_entity_releases(etype, e)
        if conf.cache.entities[etype].has_key(e):
            old = conf.cache.entities[etype][e]
            diff = new.difference(old)
            if len(diff) > 0:
                new_releases[e] = diff
                conf.cache.update(etype, e, diff)
        else:
            new_releases[e] = new
            conf.cache.update(etype, e, new)
    return new_releases



def parse_cmd():
    """ parse the command line options and load the files """
    p = optparse.OptionParser()
    home = os.environ['HOME']

    p.add_option('--apikey', '-k',
            default=home + "/.zelfratz/api-key",
            help='file that contains the api key',
            dest='apikey')

    p.add_option('--artists', '-a',
            default=home +'/.zelfratz/artists',
            help='file that contains a list of artists',
            dest='artists')

    p.add_option('--labels' , '-l',
            default=home +'/.zelfratz/labels',
            help='file that contains a list of labels',
            dest='labels')

    p.add_option('--cache', '-c',
            default=home + '/.zelfratz/cache',
            help='file to use as cache',
            dest='cache_file')

    p.add_option('--debug', '-d',
            action='store_true',
            default=False,
            help='output debugging information',
            dest='debug')

    p.add_option('--version, ', '-v',
            action='store_true',
            default=False,
            help='print version and exit',
            dest='version')

    options, arguments = p.parse_args()

    if options.version:
        print "zelfratz ", VERSION
        print "(!C) 2009 ", AUTHOR
        sys.exit()

    key = read_key_from_file(options.apikey)
    artists = read_list_from_file(options.artists)
    labels = read_list_from_file(options.labels)
    cache = read_cache(options.cache_file)

    conf = configuration(options.cache_file, cache, key, debug=options.debug)
    return (conf, artists, labels)

def main():
    global conf
    conf, artists, labels = parse_cmd()
    new_rel_artists = check_updates_artists(artists)
    new_rel_labels = check_updates_labels(labels)
    print "The following artists have released new material:"
    print_entity_releases(ARTIST, new_rel_artists)
    print "The following labels have released new material:"
    print_entity_releases(LABEL, new_rel_labels)
    write_cache(conf.cache, conf.cache_file)

if __name__ ==  "__main__":
    main()

