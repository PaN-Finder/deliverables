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


import requests
import json
import os
import urllib.parse
import datetime
import random
from bs4 import BeautifulSoup
import re
from playwright.sync_api import sync_playwright, expect
from IPython.display import display, JSON

print("Retrieving ESRF data for OSCARS PaN-Finder project - Task 1 - Step 1")
print(datetime.datetime.now().isoformat())
print("----------------------------------------------------------")

# PaNOSC API url 
panosc_data_provider_url = "https://icatplus.esrf.fr/api"
print("PaNOSC Data Provider Url : " + panosc_data_provider_url)


# Parameters to batch load all the public documents available
initial_skip = 0
batch_limit = 1000


# Prepare all the endpoints needed to retrieve documents (both from PaNOSC and ESRF catalogue) and realted information such datasets, files and samples
panosc_documents_url = urllib.parse.urljoin(panosc_data_provider_url + "/", "Documents")
panosc_documents_count_url = urllib.parse.urljoin(panosc_documents_url + "/", "count")

print("Urls used to retrieve data");
print(f" - PaNOSC Documents            : {panosc_documents_url}")
print(f" - PaNOSC Documents Count      : {panosc_documents_count_url}")


# Retrieve the number of PaNOSC documents
res = requests.get(panosc_documents_count_url)
assert(res.status_code == 200)
number_of_panosc_documents = res.json()["count"]
print("Number of public documents available : " + str(number_of_panosc_documents))

# Retrieve all the PaNOSC documents
print("Starting panosc document collection...")
panosc_documents = []
keep_going = True
skip = initial_skip
while keep_going:
    params = {
        "filter" : json.dumps({
            "skip" : skip,
            "limit" : batch_limit
        })
    }
    res = requests.get(
        panosc_documents_url,
        params = params
    )
    current_batch = res.json()
    keep_going = len(current_batch) == batch_limit
    panosc_documents += current_batch
    print(".",end="")
    skip += len(current_batch)

print("")
print("Panosc documents collected")

if len(panosc_documents) == number_of_panosc_documents:
  print("Correct number of documents collected")
else:
  print("Number of PaNOSC documents collected does not match with the count provided")


print("Preparing document list for output...")
output_data = [
    {
        "panosc" : panosc_document
    }
    for panosc_document
    in panosc_documents
]
print("Documents list prepared")

data_file_name = "../data/esrf/oscars_pan_finder_esrf_panosc_documents.json"
print("Saving saving PaNOSC documents in file: " + data_file_name)

with open(data_file_name,'w') as fh:
    json.dump(output_data,fh)

print("----------------------------------------------------------")
print(datetime.datetime.now().isoformat())
print("ESRF PaNOSC documents for OSCARS PaN-Finder project retrieved and saved")


