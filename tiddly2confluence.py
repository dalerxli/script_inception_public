#!/usr/bin/env python
# script to port tiddlywiki code to confluence wiki
import re

# TODO:
# ! -> h1.
# !! -> h2.
# !!! -> h3.
# !!!! -> h4.

# {{{ -> {code}
# }}} -> {code}

input = open(filename);
fulltext = input.read();
input.close();
