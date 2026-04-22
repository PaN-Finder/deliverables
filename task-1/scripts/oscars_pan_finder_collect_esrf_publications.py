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
# The list of publications retrieved will be saved in a file named:or
#  ../data/esrf/esrf_publications.json
# If instructed, for each entry it will collect additional information running the script oscars_pan_finder_collect_esrf_publication
# which will save all the information retrieved for a single entry in a dedicated file
#
# Usage:
#  oscars_pan_finder_collect_esrf_publications
#   -o, --output-file = Save PaNOSC entries in file. Default="../data/esrf/oscars_pan_finder_esrf_publications.json"
#   -e, --retrieve-entries = Retrieves all the entries and save them to individual files
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
        "-o","--output-file",
        help="Save PaNOSC entries in file",
        dest="output_file",
        default="../data/esrf/oscars_pan_finder_esrf_publications.json",
        type=str
    )
    parser.add_argument(
        "-e", "--retrieve-entries",
        help="Retrieves all the entries and save them to individual files",
        dest="retrieve_entries",
        action="store_true",
    )
    parser.add_argument(
        "-c","--portal-conf-file",
        help="Path to the file containing the configuration for the portal. It will be created if it does not exists.",
        dest="conf_file",
        default="../data/esrf/esrf_data_portal_config.json",
        type=str
    )
    args = parser.parse_args()
    output_file = os.path.abspath(args.output_file)
    retrieve_entries = args.retrieve_entries
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
    print(f" - Output File                    : {output_file}")
    print(f" - Retrieve Entries               : {retrieve_entries}")
    print(f" - Configuration File             : {conf_file}")
    print(f" - Python Interpreter             : {python_path}")

    # establish session
    print("Retrieving session - BEGIN")
    config = settings.get_config(conf_file)
    session_id = settings.get_session(user_info=config["authentication"]["anonymous"])
    print(f" - Session Id                     : {session_id}")
    print("Retrieving session - END")

    print("Settings URL - BEGIN")
    catalogue_url = re.sub("<SESSION_TOKEN>", session_id, settings.catalogue_base_url)
    print(f" - Catalogue URL                  : {catalogue_url}")
    datacollection_url = urllib.parse.urljoin(catalogue_url, "datacollection")
    print(f" - Data Collection URL            : {datacollection_url}")
    print("Settings URL - END")

    # Retrieve all ESRF publication entries
    print("Collecting ESRF publications - BEGIN")
    publication_documents = []
    keep_going = True
    skip = settings.initial_skip
    while keep_going:
        # https://icatplus.esrf.fr/catalogue/a1a4c6c7-a77c-44cc-b06e-4cd9439c1dfd/datacollection
        #  ?
        #   type = datacollection &
        #   sortBy = DATE &
        #   sortOrder = -1 &
        #   limit = 20 &
        #   skip = 0
        params = {
            "type" : "datacollection",
            "sortBy" : "DATE",
            "sortOrder" : -1,
            "skip" : skip,
            "limit" : settings.batch_limit
        }
        res = requests.get(
            datacollection_url,
            params = params
        )
        current_batch = res.json()
        keep_going = len(current_batch) == settings.batch_limit
        publication_documents += current_batch
        print(".",end="")
        skip += len(current_batch)

    print("")
    print("Collecting ESRF publications - END")
    print("Collected " + str(len(publication_documents)) + " documents")

    print("Cleaning entries - BEGIN")
    publication_documents = [
        settings.extract_fields(
            pub,
            ["createTime", "modTime", "dataCollectionDatasets", "doi", "parameters"]
        )
        for pub
        in publication_documents
    ]
    print("Cleaning entries - END")

    print("Saving ESRF publication documents in file: " + output_file)
    with open(output_file,'w') as fh:
        json.dump(publication_documents,fh)

    if retrieve_entries:
        for entry in publication_documents:
            print(f"Collecting publication with DOI {entry['doi']}")
            if isinstance(entry["doi"],str) and entry["doi"]:
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

    print("----------------------------------------------------------")
    print(datetime.datetime.now().isoformat())
    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_panosc_documents - END")

if __name__ == "__main__":
    main()
