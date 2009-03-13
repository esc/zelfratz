# "zelfratz" is (!C) 2009 Valentin 'esc' Haenel
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import unittest, pickle
import zelfratz


def enable_override(func):
    """ decorator to override zelfratz.get_entity_releases """
    def wrapper(*arg, **kwargs):
        # override to avoid downloading from digital tunes
        back = zelfratz.get_entity_releases
        zelfratz.get_entity_releases = zelfratz_get_entity_releases_OVERRIDE
        # call function
        res = func(*arg , **kwargs)
        # put original back in place
        zelfratz.get_entity_releases = back
        return res
    return wrapper

def zelfratz_get_entity_releases_OVERRIDE(type, entity):
    print "zelfratz_get_entity_releases_OVERRIDE successful"
    if type == zelfratz.LABEL:
        return load_xml_from_file('releases_by_label.xml')
    else:
        return load_xml_from_file('releases_by_artist.xml')

def unpickle(filename):
    file = open(filename,'r')
    ob = pickle.loads(pickle.load(file))
    file.close()
    return ob

def load_xml_from_file(filename):
    file = open(filename)
    rel = set(zelfratz.parse_release_xml(file.read()))
    file.close()
    return rel

class test_zelfratz(unittest.TestCase):

    def setUp(self):
        self.pyro = 'pyro'
        self.digital_venom = 'digital_venom'

    def test_create_api_request(self):
        zelfratz.conf = zelfratz.configuration(None,None,'666')
        target = "http://api.digital-tunes.net/releases/by_artist/pyro?key=666"
        result = zelfratz.create_api_request(zelfratz.ARTIST,self.pyro)
        self.assertEqual(target,result,msg="test_create_api_request failed with ARTIST")

        target = "http://api.digital-tunes.net/releases/by_label/digital_venom?key=666"
        result = zelfratz.create_api_request(zelfratz.LABEL,self.digital_venom)
        self.assertEqual(target,result,msg="test_create_api_request failed with LABEL")

    def test_read_funcs(self):
        target = '0000000000'
        result = zelfratz.read_key_from_file('test_key')
        self.assertEqual(target,result,msg="read_key_from_file_failed")

        target = [self.pyro]
        result = zelfratz.read_list_from_file('test_artists')
        self.assertEqual(target,result,msg="read_list_from_file failed for artists")

        target = [self.digital_venom]
        result = zelfratz.read_list_from_file('test_labels')
        self.assertEqual(target,result,msg="read_list_from_file failed for labels")

    def test_parse_xml(self):
        self.helper_test_parse_xml('pickled_releases',
                'releases_by_label.xml',zelfratz.parse_release_xml)
        self.helper_test_parse_xml('pickled_tracks',
                'tracks_by_artist.xml',zelfratz.parse_track_xml)

    def helper_test_parse_xml(self,pickled_stuff,xml_stuff,parse_func):
        target = unpickle(pickled_stuff)
        file = open(xml_stuff,'r')
        result = parse_func(file.read())
        file.close()
        self.assertEqual(target,result,msg=parse_func.func_name + 'failed')

    def test_zdata(self):
        pass

    @enable_override
    def test_check_updates(self):
       # load an empty cache
        zelfratz.conf = zelfratz.configuration(None,zelfratz.zdata(),None)
        # this will invoke the OVERRIDE and add stuff in xml to cache
        zelfratz.check_updates_artists([self.pyro])
        zelfratz.check_updates_labels([self.digital_venom])
        # now comapare the cache to one thats on disk
        target = zelfratz.read_cache('test_cache')
        result = zelfratz.conf.cache
        self.assertEqual(target,result,msg="test_check_updates failed")

    @enable_override
    def test_difference(self):
        # load apparently old artist info into cache
        zelfratz.conf = zelfratz.configuration(None,zelfratz.zdata(),None)
        rel = load_xml_from_file('old_releases_by_artist.xml')
        zelfratz.conf.cache.update_artist(self.pyro,rel)
        # load apparently old label info into cache
        rel = load_xml_from_file('old_releases_by_label.xml')
        zelfratz.conf.cache.update_label(self.digital_venom,rel)
        # now run the update methods and see what the return
        result = zelfratz.check_updates_artists([self.pyro])
        target = unpickle('pickled_artist_updates')
        self.assertEqual(target,result,msg="test_difference failed for artists")
        result = zelfratz.check_updates_labels([self.digital_venom])
        target = unpickle('pickled_label_updates')
        self.assertEqual(target,result,msg="test_difference failed for labels")

if __name__ == '__main__':
    unittest.main()

