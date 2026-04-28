#!/usr/bin/env python
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Data collector for publications from PaN data provider:
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script will perform the data collection only if run in the correct python environment.
# This script leverage the ESRF data portal API to collect all the public publication.
# This script will not perform the collection of the list of DOIs, but it will rely on a file previously saved
# If not specified otherwise, The list of publications should be in a file named:
#  "../data/esrf/oscars_pan_finder_esrf_publications.json"
#
# Usage:
#  oscars_pan_finder_collect_esrf_publications
#   -i, --input-file = File with DOIs entries previously saved. Default="../data/esrf/oscars_pan_finder_esrf_publications.json"
#   -c, --portal-conf-file = Path to the file containing the configuration for the portal. It will be created if it does not exists.
#                            default="../data/esrf/esrf_data_portal_config.json",
#
# Version: 1.0
#
#
#
# -------------------------------------------------
# This file is part of deliverables for the PaN-Finder project, founded by the OSCARS project and the European Union .
# PaN-Finder is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# PaN-Finder is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with PaN-Finder.
# If not, see <https://www.gnu.org/licenses/>.
#

import subprocess
import urllib

import requests
import json
import os
#import urllib.parse
import datetime
import random
from bs4 import BeautifulSoup
import re
#from playwright.sync_api import sync_playwright, expect
from IPython.display import display, JSON
import argparse
import sys

import oscars_pan_finder_settings_esrf as settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i","--input-file",
        help="Input file with all the DOI entries",
        dest="input_file",
        default="../data/esrf/oscars_pan_finder_esrf_publications.json",
        type=str
    )
    parser.add_argument(
        "-c","--portal-conf-file",
        help="Path to the file containing the configuration for the portal. It will be created if it does not exists.",
        dest="conf_file",
        default="../data/esrf/esrf_data_portal_config.json",
        type=str
    )
    args = parser.parse_args()
    input_file = os.path.abspath(args.input_file)
    conf_file = args.conf_file

    python_path = sys.executable

    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_publications - BEGIN")
    print(datetime.datetime.now().isoformat())
    print("----------------------------------------------------------")

    print("Urls used to retrieve data");
    print(f" - ESRF Data Portal base Url      : {settings.data_portal_api_base_url}")
    print(f" - ESRF Session Url               : {settings.session_url}")
    print(f" - ESRF Catalogue base Url        : {settings.catalogue_base_url}")
    print(f" - ESRF Data Portal Configuration : {settings.data_portal_config_url}")
    print(f" - Input File                     : {input_file}")
    print(f" - Configuration File             : {conf_file}")
    print(f" - Python Interpreter             : {python_path}")

    # Load entries from file
    print("Loading ESRF publications from file - BEGIN")
    with open(input_file,'r') as fh:
        publication_documents = json.load(fh)
    print("Loading ESRF publications from file - END")
    print("Loaded " + str(len(publication_documents)) + " documents")

    print("Saving ESRF publication documents in file: " + input_file)
    with open(input_file,'w') as fh:
        json.dump(publication_documents,fh)

    error_dois = []
    for entry in publication_documents:
        print(f"Collecting publication with DOI {entry['doi']}")
        try:
            if isinstance(entry["doi"], str) and entry["doi"]:
                print("BEGIN ============")
                subprocess.run([
                    python_path,
                    os.path.abspath("./oscars_pan_finder_collect_esrf_publication.py"),
                    "-d",
                    entry["doi"],
                    "-p",
                    json.dumps(entry),
                    "-f",
                    "-s",
                    "-u"]
                )
                print("END ==============")
        except Exception as e:
            error_dois.append(entry['doi'])
            print(f"Error collecting publication with DOI {entry['doi']}")
            print(e)

    print(f"Collection errors")
    print(f" - Number of errors {len(error_dois)}")
    print(f" - DOIs with errors ")
    print(json.dumps(error_dois))
    print("----------------------------------------------------------")
    print(datetime.datetime.now().isoformat())
    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_panosc_documents - END")

if __name__ == "__main__":
    main()
