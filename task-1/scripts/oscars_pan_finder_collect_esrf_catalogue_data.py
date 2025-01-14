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
# This script to leverage the ESRF data portal to collect additional information on each PaNOSC document.
# Each document is saved in a separate file named:
#  ../data/esrf/esrf_document_<pid>.json
#
# Usage: oscars_pan_finder_collect_esrf_catalogue_data <panosc_documents>.json [<number_of_documents_to_process>]
#
# - panosc_documents.json is the json file containing the PaNOSC documents saved by the script oscars_pan_finder_collect_esrf_panosc_documents.py
# - number_of_documents_to_process is the number of documents to process in this run. 
#   Please set it to anynumber less than or equal to zero to download all the documents
#
# documents that already present in the folder are not downloaded
# 
# Version: 3.0
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
import sys

panosc_documents_file = sys.argv[1]
number_of_documents_to_process = int(sys.argv[2]) if len(sys.argv)>2 else 5

print("Retrieving ESRF data for OSCARS PaN-Finder project - Task 1 - Step 1")
print(datetime.datetime.now().isoformat())
print("----------------------------------------------------------")
print("Input arguments:")
print(" - PaNOSC Document input file     : {}".format(panosc_documents_file))
print(" - Number of documents to process : {}".format(number_of_documents_to_process))
print("")

# PaNOSC API url 
panosc_data_provider_url = "https://icatplus.esrf.fr/api"
print("PaNOSC Data Provider Url : " + panosc_data_provider_url)


# Internal data API url
data_portal_base_url = "https://data.esrf.fr/investigation/<PID>/datasets"
print("Data portal base url : " + data_portal_base_url)


# Parameters to batch load all the public documents available
initial_skip = 0
batch_limit = 1000


# Prepare all the endpoints needed to retrieve documents (both from PaNOSC and ESRF catalogue) and realted information such datasets, files and samples
doi_base_url = urllib.parse.urljoin(panosc_data_provider_url + "/../", "doi/<DOI>/")
datacite_base_url = urllib.parse.urljoin(doi_base_url, "json-datacite")
catalogue_url = urllib.parse.urljoin(panosc_data_provider_url + "/", "../catalogue/<SESSION_TOKEN>/")
catalogue_investigation_url = urllib.parse.urljoin(catalogue_url, "investigation")
catalogue_dataset_url = urllib.parse.urljoin(catalogue_url, "dataset")
catalogue_sample_url = urllib.parse.urljoin(catalogue_url, "samples")
catalogue_datafile_url = urllib.parse.urljoin(catalogue_url, "datafile")

print("Urls used to retrieve data");
print(f" - Datacite base url           : {datacite_base_url}")
print(f" - Catalogue base url          : {catalogue_url}")
print(f" - Catalogue Investigation url : {catalogue_investigation_url}")
print(f" - Catalogue Dataset url       : {catalogue_dataset_url}")
print(f" - Catalogue Sample url        : {catalogue_sample_url}")
print(f" - Catalogue Datafile url      : {catalogue_datafile_url}")


# retrieve list of panosc documents from file
print("")
print("Input file with PaNOSC documents : ", panosc_documents_file)
with open(panosc_documents_file,"r") as fh:
    input_data = json.load(fh)

number_of_panosc_documents = len(input_data)
print("Number of panosc documents : " + str(number_of_panosc_documents))

number_of_documents_to_process = len(input_data) \
    if number_of_documents_to_process<1 \
    else number_of_documents_to_process
print("Updated number of documents to process : {}".format(number_of_documents_to_process))

# Find a document/proposal that is not in its embargo period
print("Selecting random document to initiate session on data portal")
temp_document = random.choice([
    document["panosc"] 
    for document 
    in input_data
    if (
        document["panosc"]["releaseDate"] is None
        or datetime.datetime.fromisoformat(document["panosc"]["releaseDate"]) <= datetime.datetime.now(datetime.UTC)
    )
])

print("PID of document selected : {}".format(temp_document['pid']))

# Open the data portal so we can obtain a session id to use for collecting all other information
data_portal_url = re.sub("<PID>",temp_document['pid'],data_portal_base_url)
print("Document data portal url : " + data_portal_url)


# To be sure to collect all the api calls, we wait for the data portal app (which is react) to populate the last  download button in list of datasets
# 
# We use the css selector to select the button:  
# `.table > tbody > tr:last-child > td:last-child > div:nth-child(2) > button`
# 
# The original selector provided by the browser was:  
# `.table > tbody:nth-child(2) > tr:nth-child(20) > td:nth-child(8) > div:nth-child(2) > button:nth-child(1)`

data_requests = []
data_portal_page = None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.on("response", lambda response: data_requests.append({
        "status" : response.status, 
        "url" : response.url
    }))
    #await page.goto(data_portal_url, wait_until="commit", timeout=10000000)
    page.goto(data_portal_url)
    button = page.locator('.table > tbody > tr:last-child > td:last-child > div:nth-child(2) > button')
    try:
        expect(button).to_be_attached()    
    except:
        pass

    data_portal_page = page.content()

    page.context.close()
    browser.close()


catalogue_requests = [item for item in data_requests if "catalogue" in item['url']]
assert len(catalogue_requests) > 0, "No background requests intercepted from data catalogue app"
session_token = urllib.parse.urlparse(catalogue_requests[0]["url"]).path.split('/')[2]
assert session_token, "No session token retrieved"
print("Current session token : " + session_token)



# Functions to retrieve the different pieces of information for a single document
def retrieve_datacite_info(doi):
    print(" - Retrieve Datacite Info")
    if doi:
        try:
            datacite_url = re.sub("<DOI>",doi,datacite_base_url)
            print(" -- Datacite url : " + datacite_url)
            res = requests.get(datacite_url)
            print(" -- Request result : ", res.status_code)
            return res.json()
        except:
            return "Error retrieving resource"
    else:
        return "Not doi available"

def retrieve_investigation(session_token,pid):
    """
    Collect more info regarding the investigation.

    Post a GET request to ESRF catalogue as follows:
    ```
    https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/investigation?ids=144479045
    ```
    """
    print(" - Retrieve Investigation")

    if not session_token:
        return "Session token not provided"
    elif not pid:
        return "Investigation id not provided"

    try:
        session_investigation_url = re.sub("<SESSION_TOKEN>",session_token,catalogue_investigation_url)
        print(" -- Session Investigation Url : " + session_investigation_url)

        params = {
            "ids" : pid
        }

        res = requests.get(
            url = session_investigation_url,
            params = params
        )
        print(" -- Request result : ", res.status_code)

        investigation_data = remove_fields(res.json()[0],["meta","type"])
        return investigation_data
    except:
        return "Error retrieving resource"
            

def remove_fields(initem,fields):
    outitem = dict(initem)
    for field in fields:
        if field in outitem.keys():
            del outitem[field]
    return outitem

def fix_dataset_parameter(initem):
    outitem = dict(initem)
    del outitem["id"]
    del outitem["datasetId"]
    return outitem

def fix_dataset(initem):
    outitem = dict(initem)
    outitem = remove_fields(outitem,["investigation","meta"])
    outitem["parameters"] = [fix_dataset_parameter(parameter) for parameter in outitem["parameters"]]
    return outitem
    
def retrieve_datasets(session_token,pid):
    """
    Retrieve all the datasets associated with this document

    It does a GET request to ESRF catalogue as follow:
    ```
    https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/dataset?investigationIds=144479045&datasetType=acquisition&sortBy=STARTDATE&sortOrder=-1&nested=true&limit=20&skip=0
    ```
    """
    print(" - Retrieve Dataset")

    if not session_token:
        return "Session token not provided"
    elif not pid:
        return "Investigation id not provided"

    try:
        session_datasets_url = re.sub("<SESSION_TOKEN>",session_token,catalogue_dataset_url)
        print(" -- Session Datasets Url : " + session_datasets_url)

        params = {
            "investigationIds" : pid,
            "datasetType" : "acquisition",
            "sortBy" : "STARTDATE",
            "sortOrder" : -1,
            "nested" : True
        }

        res = requests.get(
            url = session_datasets_url,
            params = params
        )
        print(" -- Request result : ", res.status_code)

        datasets_data = [fix_dataset(item) for item in res.json()]
        return datasets_data
    except:
        return "Error retrieving resource"


# 
# samples can be found from the documents/datasets information
#
# def retrieve_samples(session_token,pid):
#     """
#     Retrieve all the samples associated with this document

#     It does a GET request to ESRF catalogue as follow:
#     ```
#     https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/samples?investigationId=144479045&search=&limit=20
#     ```
#     """
#     print(" - Retrieve Samples")

#     if not session_token:
#         return "Session token not provided"
#     elif not pid:
#         return "Investigation id not provided"

#     try:
#         session_samples_url = re.sub("<SESSION_TOKEN>",session_token,catalogue_sample_url)
#         print(" -- Session Samples Url : " + session_samples_url)

#         params = {
#             "investigationId" : pid
#         }

#         res = requests.get(
#             url = session_samples_url,
#             params = params
#         )
#         print(" -- Request result : ", res.status_code)

#         samples_data = res.json()
#         return samples_data
#     except:
#         return "Error retrieving resource"
        

#
# We skip retrieving data files as their number is quite high and resource intense
# also they are not key to our system, at least for now
#
# def retrieve_datafiles(session_datafiles_url,pid):
#     """
#     Retrieve all the datafiles associated with this document and its datasets

#     It does with a GET request to ESRF catalogue for each dataset as follow:
#     ```
#     https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/datafile?datasetId=514590601&limit=1
#     ```
#     """
#     print(" - Retrieve Datafiles")

#     if not session_datafiles_url:
#         return "Url not provided"
#     elif not pid:
#         return "dataset id not provided"

#     try:
#         params = {
#             "datasetId" : pid
#         }
    
#         res = requests.get(
#             url = session_datafiles_url,
#             params = params
#         )
#         print(" -- Request result : ", res.status_code)

#         return res.json()

#     except:
#         return "Error retrieving resource"

def retrieve_all_data(session_token,panosc_document):
    print("Retrieve all data")
    pid = panosc_document["pid"]
    doi = panosc_document["doi"]
    print("PID {} - DOI {}".format(pid,doi))
    output = {
        "panosc" : panosc_document,
        "datacite" : retrieve_datacite_info(doi),
        "catalogue" : retrieve_investigation(session_token,pid),
#        "samples" : retrieve_samples(session_token,pid),
        "datasets" : retrieve_datasets(session_token,pid)
    }
    

    # session_datafiles_url = re.sub("<SESSION_TOKEN>",session_token,catalogue_datafile_url)
    # print(" - Session Datafiles Url : " + session_datafiles_url)

    # datasets = retrieve_datasets(session_token,pid)
    # print(f" - Number of datasets : {len(datasets):10} ")
    # if isinstance(datasets,list):
    #     output["datasets"] = {}
    #     output["datafiles"] = {}
    #     for dataset in datasets:
    #         did = dataset["id"]
    #         print(f" -- Dataset : {did} ")
            
    #         output["datasets"][did] = dataset
    #         output["datafiles"][did] = retrieve_datafiles(session_datafiles_url,did)

    return output

data_folder = os.path.abspath("../data/esrf/")

print("Processing {} documents".format(number_of_documents_to_process))
document_counter = 1
for document in input_data[:number_of_documents_to_process]:
    print("-"*20)
    print("Document {} of {}".format(document_counter,number_of_documents_to_process))

    pid = document["panosc"]["pid"]
    print("Check if file has already been acquired")
    
    
    document_file = [f for f in os.listdir(data_folder) if "_" + pid + "_" in f]
    if document_file:
        print(" - document already retrieved {}".format(document_file[0]))
    else:
        document_file =  data_folder + "/esrf_document_" + pid + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        print("Saving data in file: " + document_file)

        output_data = retrieve_all_data(session_token,document["panosc"])

        with open(document_file,'w') as fh:
            json.dump(output_data,fh)

    document_counter += 1

print("Processed all documents")


print("----------------------------------------------------------")
print(datetime.datetime.now().isoformat())
print("ESRF catalogue data for OSCARS PaN-Finder project retrieved and saved")

