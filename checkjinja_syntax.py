#!/usr/bin/env python

# filename: check_my_jinja.py
import sys
from jinja2 import Environment

env = Environment()
with open(sys.argv[1]) as template:
    env.parse(template.read())
