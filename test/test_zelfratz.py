import unittest
import zelfratz

class test_zelfratz(unittest.TestCase):

    def test_create_api_request(self):
        target = "http://api.digital-tunes.net/releases/by_artist/pyro?key=666"
        result = zelfratz.create_api_request(zelfratz.ARTIST,'pyro','666')
        self.assertEqual(target,result,msg="test_create_api_request failed with ARTIST")

        target = "http://api.digital-tunes.net/releases/by_label/digital_venom?key=666"
        result = zelfratz.create_api_request(zelfratz.LABEL,'digital_venom','666')
        self.assertEqual(target,result,msg="test_create_api_request failed with LABEL")

    def test_read_funcs(self):
        target = '0000000000'
        result = zelfratz.read_key_from_file('test_key')
        self.assertEqual(target,result,msg="read_key_from_file_failed")

        target = "pyro"
        result = zelfratz.read_key_from_file('test_artists')
        self.assertEqual(target,result,msg="read_list_from_file failed for artists")

        target = "digital_venom"
        result = zelfratz.read_key_from_file('test_labels')
        self.assertEqual(target,result,msg="read_list_from_file failed for labels")



if __name__ == '__main__':
    unittest.main()

