# "zelfratz" is (!C) 2009 Valentin 'esc' Haenel
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import unittest, pickle
import zelfratz

class test_zelfratz(unittest.TestCase):

    def test_create_api_request(self):
        zelfratz.key = '666'
        target = "http://api.digital-tunes.net/releases/by_artist/pyro?key=666"
        result = zelfratz.create_api_request(zelfratz.ARTIST,'pyro')
        self.assertEqual(target,result,msg="test_create_api_request failed with ARTIST")

        target = "http://api.digital-tunes.net/releases/by_label/digital_venom?key=666"
        result = zelfratz.create_api_request(zelfratz.LABEL,'digital_venom')
        self.assertEqual(target,result,msg="test_create_api_request failed with LABEL")

    def test_read_funcs(self):
        target = '0000000000'
        result = zelfratz.read_key_from_file('test_key')
        self.assertEqual(target,result,msg="read_key_from_file_failed")

        target = ["pyro"]
        result = zelfratz.read_list_from_file('test_artists')
        self.assertEqual(target,result,msg="read_list_from_file failed for artists")

        target = ["digital_venom"]
        result = zelfratz.read_list_from_file('test_labels')
        self.assertEqual(target,result,msg="read_list_from_file failed for labels")

    def test_parse_xml(self):
        self.helper_test_parse_xml('pickled_releases',
                'releases_by_label.xml',zelfratz.parse_release_xml)
        self.helper_test_parse_xml('pickled_tracks',
                'tracks_by_artist.xml',zelfratz.parse_track_xml)

    def helper_test_parse_xml(self,pickled_stuff,xml_stuff,parse_func):
        file = open(pickled_stuff,'r')
        target = pickle.loads(pickle.load(file))
        file.close()
        file = open(xml_stuff,'r')
        result = parse_func(file.read())
        file.close()
        self.assertEqual(target,result,msg=parse_func.func_name + 'failed')

    def test_zdata(self):
        pass

    def test_check_updates(self):
        # override to avoid downloading from digital tunes
        zelfratz.get_entity_releases = zelfratz_get_entity_releases_OVERRIDE
        # load an empty cache
        zelfratz.cache = zelfratz.zdata()
        # this will invoke the OVERRIDE and add stuff in xml to cache
        zelfratz.check_updates_artists(['pyro'])
        zelfratz.check_updates_labels(['digital_venom'])
        # now comapre the cache to one thats on disk
        file = open('test_cache','r')
        target = pickle.loads(pickle.load(file))
        file.close()
        result = zelfratz.cache
        self.assertEqual(target,result,msg="test_check_updates failed")



def zelfratz_get_entity_releases_OVERRIDE(type, entity):
    print "zelfratz_get_entity_releases_OVERRIDE successful"
    file = None
    if type == zelfratz.LABEL:
        file = open('releases_by_label.xml','r')
    else:
        file = open('releases_by_artist.xml','r')
    s = set(zelfratz.parse_release_xml(file.read()))
    file.close()
    return s

if __name__ == '__main__':
    unittest.main()

