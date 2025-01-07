#!/usr/bin/env python
# coding: utf-8

# OSCARS PaN-Finder script
# 
# Retrieve all publicly accessible and published data from data provider: ESRF
# Data is retrieved from PaNOSC search interface and saved to a json files to be used at a later stage
# 
# Version: 1.0

import requests
import json
import os
import urllib.parse
import datetime
import random
from bs4 import BeautifulSoup
import re
from playwright.sync_api import sync_playwright, expect
#from playwright.async_api import async_playwright, expect
from IPython.display import display, JSON


# PaNOSC API url 
data_provider_url = "https://icatplus.esrf.fr/api"
print("Data provider url : " + data_provider_url)


# DOI landing page url (not used)
doi_url = "https://doi.esrf.fr/"
print("DOI landing page url : " + doi_url)

# Internal data API url
data_portal_base_url = "https://data.esrf.fr/investigation/<PID>/datasets"
print("Data portal base url : " + data_portal_base_url)


# Parameters to batch load all the public documents available
initial_skip = 0
batch_limit = 1000


# Prepare all the endpoints needed to retrieve documents (both from PaNOSC and ESRF catalogue) and realted information such datasets, files and samples
panosc_documents_url = urllib.parse.urljoin(data_provider_url + "/", "Documents")
panosc_documents_count_url = urllib.parse.urljoin(panosc_documents_url + "/", "count")
panosc_datasets_url = urllib.parse.urljoin(data_provider_url + "/", "datasets")
doi_base_url = urllib.parse.urljoin(data_provider_url + "/../", "doi/<DOI>/")
datacite_base_url = urllib.parse.urljoin(doi_base_url, "json-datacite")
#reports_base_url = urllib.parse.urljoin(doi_base_url, "reports")
catalogue_url = urllib.parse.urljoin(data_provider_url + "/", "../catalogue/<SESSION_TOKEN>/")
catalogue_investigation_url = urllib.parse.urljoin(catalogue_url, "investigation")
catalogue_dataset_url = urllib.parse.urljoin(catalogue_url, "dataset")
catalogue_sample_url = urllib.parse.urljoin(catalogue_url, "samples")
catalogue_datafile_url = urllib.parse.urljoin(catalogue_url, "datafile")

print("Listing all urls used below");
print(f" - PaNOSC Documents            : {panosc_documents_url}")
print(f" - PaNOSC Documents Count      : {panosc_documents_count_url}")
print(f" - Datacite base url           : {datacite_base_url}")
#print(f" - Reports base url            : {reports_base_url}")
print(f" - Catalogue base url          : {catalogue_url}")
print(f" - Catalogue Investigation url : {catalogue_investigation_url}")
print(f" - Catalogue Dataset url       : {catalogue_dataset_url}")
print(f" - Catalogue Sample url        : {catalogue_sample_url}")
print(f" - Catalogue Datafile url      : {catalogue_datafile_url}")


# Retrieve the number of open documents
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
    #print(f"Skip : {skip}. Params: {params}. Status Code: {res.status_code}. Url: {res.request.url}. Number of results: {len(current_batch)}. Continue: {keep_going}. Total number of datasets retrieved: {len(raw_documents)}")
    print(".",end="")
    skip += len(current_batch)

print("")
print("Panosc documents collected")

assert(len(panosc_documents) == number_of_panosc_documents)
print("Correct number of documents collected")

output_data = [
    {
        "panosc" : panosc_document
    }
    for panosc_document
    in panosc_documents
]

data_file_name = "../data/esrf_open_data_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
print("Saving data in file: " + data_file_name)

with open(data_file_name,'w') as fh:
    json.dump(output_data,fh)

