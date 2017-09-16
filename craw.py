#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import requests
import argparse
import datetime
from lxml.html import fromstring
from urllib.parse import urlparse

DEFAULT_DEPTH = 2
DEFAULT_WIDTH = 50

parser = argparse.ArgumentParser()

parser.add_argument('url', action="store")
parser.add_argument('-depth', action="store", type=int, default=DEFAULT_DEPTH)
parser.add_argument('-width', action="store", type=int, default=DEFAULT_WIDTH)
parser.add_argument('-tree', action="store_true", default=False)


visited = set()
tree = []


def valid_url(url):
    return urlparse(url).scheme != ''

def print_tree(lst, level=0):
    for l in lst[0:]:
        if type(l) is list:
            print_tree(l, level + 1)
        else:
            print('    ' * level + '+---' + l)



def visit(url, depth, width, dir, node):
    if depth < 0:
        return
    if url in visited:
        return
    else:
        visited.add(url)

    if not valid_url(url):
        if valid_url("http:" + url):
            url = "http:" + url
        elif valid_url("http://" + url):
            url = "http://" + url
        else:
            return

    title = "no_title"
    try:
        response = requests.get(url)
        content = response.content.decode('utf-8')
        title = fromstring(content).findtext('.//title')
        if title is None or title == "no_title":
            return
        if len(title) > 30:
            title = title[0:30]
        if title in visited:
            return
        elif title != "no_title":
            visited.add(title)
        for c in r'[]/\;,><&*:%=+@!#^()|?^' + '\n\r':
            title = title.replace(c, '')
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', content)

        directory = dir + '/' + title
        if not os.path.exists(directory):
            os.makedirs(directory)
        f = os.open(directory + "/" + title + ".html", os.O_CREAT | os.O_RDWR)
        os.write(f, content.encode('utf-8'))
        os.close(f)

        cnt = 0
        node.append([title])
        for u in urls:
            visit(u, depth - 1, width, directory, node[-1])
            cnt += 1
            if cnt == width:
                break

    except Exception as e:
        print("failed at", title, ": ", e)
    print("dump", title)


if __name__ == '__main__':
    args = parser.parse_args()

    directory = "data_" + datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
    if not os.path.exists(directory):
        os.makedirs(directory)

    visit(args.url, args.depth, args.width, directory, tree)

    if args.tree:
        print_tree(tree)
