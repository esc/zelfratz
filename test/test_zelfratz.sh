#!/bin/sh
# run zelfratz with test input files
#echo "testing zelfratz now!"
#echo "will now test the command line interface"
#PATH=../:$PATH zelfratz.py -k test_key -a test_artists -l test_labels
echo "will now run unit tests"
PYTHONPATH=../ python test_zelfratz.py
