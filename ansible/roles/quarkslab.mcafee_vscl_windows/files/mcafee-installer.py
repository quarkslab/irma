#!/usr/bin/python

import os
import sys
import logging
import argparse
from urllib.request import urlopen
import zipfile
import tempfile
import re

def download(url, f):
  dl = urlopen(url)
  f.write(dl.read())

def unzip(f, dest_path):
    zf = zipfile.ZipFile(f)
    zf.extractall(dest_path)

def dl_and_unzip(url, path):
    logging.debug("url: {}".format(url))
    logging.debug("path: {}".format(path))
    with tempfile.NamedTemporaryFile(prefix="irma_mcafee_") as f:
        download(url, f)
        unzip(f, path)

def do_install(args):
    dl_and_unzip(args.url, args.path)

def get_last_signature_url(url):
    dl = urlopen(url)
    dir_list = dl.read()
    regexp = re.compile(b"avvdat-.+.zip")
    m = regexp.findall(dir_list)
    if m:
        file_name = str(m[0], "utf-8")
        return file_name, os.path.join(url, file_name)

def do_update(args):
    result = get_last_signature_url(args.url)
    if result is None:
        raise Exception("Update signatures file was not found on '{}'.".format(args.url))
    updates_file_name, updates_url = result
    updates_file_path = os.path.join(args.path, updates_file_name)
    if not os.path.exists(updates_file_path):
        with open(updates_file_path, "wb") as f:
            download(updates_url, f)
        unzip(updates_file_path, args.path)

if __name__ == '__main__':
    desc = "McAfee VSCL Command Line Interface for IRMA"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-v', '--verbose', action='count', default=0)

    subparsers = parser.add_subparsers()

    install_parser = subparsers.add_parser('install', help='Installs McAfee')
    install_parser.add_argument('args', nargs=argparse.REMAINDER)
    install_parser.add_argument('-u', '--url', required=True, help='Url for download bins zipped')
    install_parser.add_argument('-p', '--path', required=True, help='Install path for McAfee')
    install_parser.set_defaults(function=do_install)

    update_parser = subparsers.add_parser('update', help='Updates McAfee')
    update_parser.add_argument('args', nargs=argparse.REMAINDER)
    update_parser.add_argument('-u', '--url', required=True, help='Url for download signatures update')
    update_parser.add_argument('-p', '--path', required=True, help='Install path for McAfee')
    update_parser.set_defaults(function=do_update)

    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    retcode = args.function(args)
    sys.exit(retcode)
