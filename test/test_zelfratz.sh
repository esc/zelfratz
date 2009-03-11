#!/bin/sh

# "zelfratz" is (!C) 2009 Valenin 'esc' Haenel
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

# run zelfratz with test input files
#echo "testing zelfratz now!"
#echo "will now test the command line interface"
#PATH=../:$PATH zelfratz.py -k test_key -a test_artists -l test_labels
echo "will now run unit tests"
PYTHONPATH=../ python test_zelfratz.py
