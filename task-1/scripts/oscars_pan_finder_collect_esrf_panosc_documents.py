#!/usr/bin/env python
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Data collector for PaNOSC data provider:
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script run the data collection script in the correct python environment.
# This script to leverage the ESRF PaNOSC search api to collect all the public available data and save them in a file named
#  ../data/esrf/oscars_pan_finder_esrf_panosc_documents.json
#
# 
# Version: 1.0
#
#
import subprocess

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

import oscars_pan_finder_settings_esrf as settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o","--output-file",
        help="Save PaNOSC entries in file",
        dest="output_file",
        default="../data/esrf/oscars_pan_finder_esrf_panosc_documents.json",
        type=str
    )
    parser.add_argument(
        "-e", "--retrieve-entries",
        help="Retrieves all the entries and save them to individual files",
        dest="include_entries",
        action="store_true",
    )
    args = parser.parse_args()
    output_file = os.path.abspath(args.output_file)
    include_entries = args.include_entries

    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_panosc_documents - BEGIN")
    print(datetime.datetime.now().isoformat())
    print("----------------------------------------------------------")

    print("Urls used to retrieve data");
    print(f" - PaNOSC Data Provider Url   : {settings.panosc_data_provider_url}")
    print(f" - PaNOSC Documents Url       : {settings.panosc_documents_url}")
    print(f" - PaNOSC Documents Count Url : {settings.panosc_documents_count_url}")
    print(f" - Output File                : {output_file}")
    print(f" - Include Entries            : {include_entries}")


    # Retrieve the number of PaNOSC documents
    res = requests.get(settings.panosc_documents_count_url)
    assert(res.status_code == 200)
    number_of_panosc_documents = res.json()["count"]
    print("Number of public documents available : " + str(number_of_panosc_documents))

    # Retrieve all the PaNOSC documents
    print("Starting panosc document collection...")
    panosc_documents = []
    keep_going = True
    skip = settings.initial_skip
    while keep_going:
        params = {
            "filter" : json.dumps({
                "skip" : skip,
                "limit" : settings.batch_limit
            })
        }
        res = requests.get(
            settings.panosc_documents_url,
            params = params
        )
        current_batch = res.json()
        keep_going = len(current_batch) == settings.batch_limit
        panosc_documents += current_batch
        print(".",end="")
        skip += len(current_batch)

    print("")
    print("Panosc documents collected")

    if len(panosc_documents) == number_of_panosc_documents:
        print("Correct number of documents collected")
    else:
        print("Number of PaNOSC documents collected does not match with the count provided")

    print("Saving saving PaNOSC documents in file: " + output_file)
    with open(output_file,'w') as fh:
        json.dump(panosc_documents,fh)

    if include_entries:
        for entry in panosc_documents:
            print(f"Collecting {entry['doi']}")
            if isinstance(entry["doi"],str) and entry["doi"]:
                print("BEGIN ============")
                subprocess.run([
                    "python",
                    os.path.abspath("./oscars_pan_finder_collect_esrf_entry.py"),
                    "-d",
                    entry["doi"],
                    "-s",
                    "-u"]
                )
                print("END ==============")

    print("----------------------------------------------------------")
    print(datetime.datetime.now().isoformat())
    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_panosc_documents - END")

if __name__ == "__main__":
    main()
