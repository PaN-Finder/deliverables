#!/usr/bin/env python
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Data collector for PaN-Finder:
# - DESY (Deutsches Elektronen-Synchrotron, https://desy.de)
#
# This script run the data collection script in the correct python environment.
# This script to leverage the ESS data catalog SciCat API to collect all the public available data and save them in a file named
# ../data/oscars_pan_finder_desy_data_<timestamp>.json
#
# 
# Version: 3.0
#
#

# import the necessary libraries
import requests
import json
import os
import urllib.parse
import datetime
import random

print("Retrieving DESY data for OSCARS PaN-Finder project - Task 1")
print(datetime.datetime.now().isoformat())
print("----------------------------------------------------------")


# DESY PaNOSC API
#panosc_data_provider_url = "https://search.panosc.ess.eu/"
#print("PaNOSC Data Provider Url: " + panosc_data_provider_url)


# Url of the public facing data catalog running at DESY
catalog_data_provider_url = "https://public-data.desy.de/api/v3"
print("Catalog Data Catalog Url: " + catalog_data_provider_url)

# batch collection settings
initial_skip = 0
batch_limit = 1000

# fields that are not necessary and needs to be deleted from the entries saved in the output file
fields_to_be_deleted_from_document = ["thumbnail","history"]

# Endpoints to retrieve all the data
#panosc_documents_url = urllib.parse.urljoin(panosc_data_provider_url + "/", "documents")
#panosc_documents_count_url = urllib.parse.urljoin(panosc_documents_url + "/", "count")
#panosc_datasets_url = urllib.parse.urljoin(panosc_data_provider_url + "/", "datasets")
catalog_publisheddata_url = urllib.parse.urljoin(catalog_data_provider_url + "/", "publisheddata")
catalog_publisheddata_count_url = urllib.parse.urljoin(catalog_publisheddata_url + "/", "count")
catalog_datasets_url = urllib.parse.urljoin(catalog_data_provider_url + "/", "datasets")

print("Urls used to retrieve data");
#print(f" - PaNOSC Documents             : {panosc_documents_url}")
#print(f" - PaNOSC Documents Count       : {panosc_documents_count_url}")
#print(f" - PaNOSC Datasets              : {panosc_datasets_url}")
print(f" - Catalog Published Data       : {catalog_publisheddata_url}")
print(f" - Catalog Published Data Count : {catalog_publisheddata_count_url}")
print(f" - Catalog Dataset              : {catalog_datasets_url}")



# retrieve the count of open documents present in the catalog
res = requests.get(catalog_publisheddata_count_url)
assert(res.status_code == 200)
number_of_open_documents = res.json()["count"]
print("Number of public documents available in catalog : " + str(number_of_open_documents))

# Load all publicly available data  
print("Starting open document collection...")
open_documents = []
keep_going = True
skip = initial_skip
while keep_going:
    params = {
        "limits" : json.dumps({
            "skip" : skip,
            "limit" : batch_limit
        },separators=(',', ':'))
    }
    res = requests.get(
        catalog_publisheddata_url,
        params = params
    )
    current_batch = res.json()
    keep_going = len(current_batch) == batch_limit
    open_documents += current_batch
    print(".",end="")
    skip += len(current_batch)

print("")
print("Catalog open documents collected")

# Confirm that we retrieved the correct amount of documents
assert(len(open_documents) == number_of_open_documents)
print("Correct number of open documents collected")


# Functions to retrieve individual datasets from published data record

def get_dataset(pid):
    res = requests.get(
        catalog_datasets_url + "/" + urllib.parse.quote_plus(pid)
    )
    return res.json()

def get_datasets(pids):
    return [
        get_dataset(pid)
        for pid
        in pids
    ]


# Loop on all the documents and retrieve the full record from ESS SciCat
print("Preparing raw data for task 1")
documents = []
for document in open_documents:
    for field_to_be_deleted in list(set(document.keys()).intersection(fields_to_be_deleted_from_document)):
        document.pop(field_to_be_deleted)

    entry = {
        "document" : document,
        "datasets" : get_datasets(document['pidArray'])
    }
    #    if document['id'] in panosc_documents.keys():
    #    entry['panosc'] = panosc_documents[document['id']]
    documents.append(entry)
    print(".",end="")


print("")
print("Raw data for task 1 preparation completed")


# Prepare data file name and save
output_data_file = os.path.abspath("../data/oscars_pan_finder_desy_data_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json")
print("Saving raw data in file : " + output_data_file)
with open(output_data_file,'w') as fh:
    json.dump(documents,fh)

print("----------------------------------------------------------")
print(datetime.datetime.now().isoformat())
print("DESY data for OSCARS PaN-Finder project retrieved and saved")


