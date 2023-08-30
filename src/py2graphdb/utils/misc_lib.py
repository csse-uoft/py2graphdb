#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: bart
"""

import glob, gc, os, re
import numpy as np
import itertools as itert

def combos_prod(l):
    return list(itert.product(*l))
def combos(l, r, replace=False):
    if replace:
        return [a for a in itert.combinations_with_replacement(l,r)]
    else:
        return [a for a in powerset(l) if len(a) == r]

def powerset(iterable):
    s = list(iterable)
    res =  [list(r2) for r2 in [list(itert.chain.from_iterable(itert.combinations(s, r) for r in range(len(s)+1)))]][0]
    res2 = []
#    print('Len = ' + str(len(res)))
    for r in res:
        res2 += [list(r)]
    return res2

def pairs(l):
    res = []
    for i in np.arange(1,len(l)-1, 1):
        res += [[l[i-1],l[i]]]
    return res
# flatten a list of lists
def flatten(l):
    return list(itert.chain.from_iterable(l))

def random_sign():
    return 1 if np.random.rand() < 0.5 else -1

def unique_all(l):
    _,idx = np.unique([str(x) for x in l], return_index=True)
    return [tuple(x) for x in np.array(l)[idx]]

def dedup(l):
    seen = set()
    smaller_l = []
    for x in l:
        if frozenset(x) not in seen:
            smaller_l.append(x)
            seen.add(frozenset(x))
    return smaller_l
def dedup_order(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def get_overlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))
# Python3 program to merge overlapping Intervals
# in O(n Log n) time and O(1) extra space
def mergeIntervals(arr, adjacent_skip=0):
    # Sorting based on the increasing order
    # of the start intervals
    # Tests
    # tmpmerge([[1,4],[3,6],[9,12],[13,17], [20,25],[25,27], [30,34],[36,40]])
    #   => [[1, 6], [9, 12], [13, 17], [20, 27], [30, 34], [36, 40]]
    # tmpmerge([[1,4],[3,6],[9,12],[13,17], [20,25],[25,27], [30,34],[36,40]], adjacent_skip=2)
    #   => [[1, 6], [9, 17], [20, 27], [30, 40]]
    # tmpmerge([[1,4],[3,6],[9,12],[13,17], [20,25],[25,27], [30,34],[36,40]], adjacent_skip=1)
    #   => [[1, 6], [9, 17], [20, 27], [30, 34], [36, 40]]
    # tmpmerge([[1,4],[3,6],[9,12],[13,17], [20,25],[25,27], [30,34],[36,40]], adjacent_skip=-2)
    #   => [[1, 4], [3, 6], [9, 12], [13, 17], [20, 25], [25, 27], [30, 34], [36, 40]]

    arr.sort(key = lambda x: x[0])
        
    # array to hold the merged intervals
    m = []
    s = -10000
    max = -100000
    for i in range(len(arr)):
        a = arr[i]
        max_check = max+adjacent_skip

        if a[0] > max_check:
            if i != 0:
                m.append([s,max])
            max = a[1]
            s = a[0]
        else:
            if a[1] >= max:
                max = a[1]
        
    #'max' value gives the last point of
    # that particular interval
    # 's' gives the starting point of that interval
    # 'm' array contains the list of all merged intervals
    if max != -100000 and [s, max] not in m:
        m.append([s, max])
    return m

def chunked_dict(it, size):
    it = iter(it)
    while True:
        p = tuple(itert.islice(it, size))
        if not p:
            break
        yield p


ORIGINAL_CONFIG = 'config/import_config_path.txt'
BACKUP_CONFIG = 'config/import_config_path.txt.bak'
UNIT_TEST_CONFIG_PATH = './config/unit_test_config.yml'
def init_test_config():
    print('>>>>> init <<<<<<<')
    import  shutil
    shutil.copyfile(ORIGINAL_CONFIG, BACKUP_CONFIG)
    _ = open(ORIGINAL_CONFIG, 'w').write(UNIT_TEST_CONFIG_PATH)

def end_unit_test_config():
    print('>>>>> end <<<<<<<')
    import os, shutil
    shutil.copyfile(BACKUP_CONFIG, ORIGINAL_CONFIG)
    os.remove(BACKUP_CONFIG)
