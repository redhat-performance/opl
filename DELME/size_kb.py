#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import random
import string

"""
Kafka allows only up to 1mb size per topic, so we are transforming script to kb

Script to generate random python dict of size 100kb, 300kb, 500kb
"""


# Function to generate random string
def generate_random_string(size):
    return "".join(random.choices(string.ascii_letters + string.digits, k=size))


# Function to generate a random dictionary of a given size (in bytes)
def generate_random_dict(size_bytes):
    size_bytes -= sys.getsizeof(dict())  # Account for dictionary overhead
    size_bytes -= sys.getsizeof("") * 2  # Account for two empty strings
    d = {}
    while sys.getsizeof(d) < size_bytes:
        key = generate_random_string(random.randint(5, 20))
        value = generate_random_string(random.randint(10, 50))
        d[key] = value
    return d


# Generate a random dictionary approximately 5kb in size
def size_of_dict(size=100):
    size_5kb = size * 1000  # 5MB in bytes
    random_dict = generate_random_dict(size_5kb)
    # Print the size of the generated dictionary in bytes
    return random_dict
