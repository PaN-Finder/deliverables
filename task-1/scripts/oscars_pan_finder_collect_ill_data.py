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
# - ILL (Institut Laue-Langevin, https://www.ill.eu/)
#
# This script run the data collection script in the correct python environment.
# This script to leverage the ILL PaNOSC interface and html data catalog to collect all the public available data and save them in a file named
#  ../data/oscars_pan_finder_ill_data_<timestamp>.json
#
# 
# Version: 1.0
#

import requests
import json
import os
import urllib.parse
import datetime
import random
from bs4 import BeautifulSoup
import re

print("Retrieving ILL data for OSCARS PaN-Finder project - Task 1")
print(datetime.datetime.now().isoformat())
print("----------------------------------------------------------")

# ILL PaNOSC API
panosc_data_provider_url = "https://fairdata.ill.fr/fairdata/api/"
print("PaNOSC Data Provider Url: " + panosc_data_provider_url)

# ILL DOI url
doi_data_provider_url = "https://doi.ill.fr/"
print("DOI Data Provider Url: " + doi_data_provider_url)


# batch collection settings
initial_skip = 0
batch_limit = 1000


# Endpoints to retrieve documents and datasets
panosc_documents_url = urllib.parse.urljoin(panosc_data_provider_url + "/", "documents")
panosc_documents_count_url = urllib.parse.urljoin(panosc_documents_url + "/", "count")
panosc_datasets_url = urllib.parse.urljoin(panosc_data_provider_url + "/", "datasets")

print("Urls used to retrieve data");
print(f" - PaNOSC Documents       : {panosc_documents_url}")
print(f" - PaNOSC Documents Count : {panosc_documents_count_url}")
print(f" - PaNOSC Datasets        : {panosc_datasets_url}")


# retrieve the count of PaNOSC documents
res = requests.get(panosc_documents_count_url)
print(res.text)
assert(res.status_code == 200)
number_of_panosc_documents = res.json()
print("Number of panosc documents available : " + str(number_of_panosc_documents))


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
    print(".",end="",flush=True)
    skip += len(current_batch)

print("")
print("{} Panosc documents collected".format(len(panosc_documents)))

if len(panosc_documents) == number_of_panosc_documents:
    print("Correct number of documents collected")
else:
    print("Number of PaNOSC documents collected does not match with the count provided")


# Functions to extract information from doi page
#
def extractAuthorInfo(item):
    output = {
        "name" : item.text.split("(")[0].strip()
    }
    links = item.find_all("a")
    if links:
        output["ids"] = []
        for link in item.find_all("a"):
            id_name = link.text
            id_url = link.attrs['href']
            id_string = id_url.split("/")[-1]

            output["ids"].append({
                "type" : id_name,
                "id" : id_string,
                "url" : id_url
            })

    return output
        
def extractAuthorsInfo(document_soup):
    authors_html = document_soup.find(
        'h4',
        class_="details-name",
        string=lambda text: "Authors" in text
    ).parent
    
    return [
        extractAuthorInfo(item2)
        for item2
        in authors_html.find_all("li")
    ]


def extractPublicationYear(document_soup):
    return document_soup.find(
        'h4',
        class_="details-name",
        string=lambda text: "Publication year" in text
    ).parent.text.strip().split(' ')[-1]


def extractCycles(document_soup):
    return [
        re.sub(" \\)",")",re.sub('  +',' ',item.text.replace('\n','').strip())) 
        for item 
        in document_soup.find(
            'h4',
            class_="details-name",
            string=lambda text: "Cycles" in text
        ).parent.find('li')
    ]


def extractInstruments(document_soup):
    return [
        {
            'name' : re.sub('  +',' ',item.text.replace('\n','').strip()),
            'url' : item.attrs['href']
        }
        for item 
        in document_soup.find(
            'h4',
            class_="details-name",
            string=lambda text: "Instruments" in text
        ).parent.find_all('a')
    ]


def extractExperimentParameters(document_soup):
    return {
        item.find('h4').text.strip() : item.find('div').text.strip().split(' ')[-1]
        for item 
        in document_soup.find(
            'h3',
            string=lambda text: "Experiment Parameters" in text
        ).parent.parent.find_all('li')
    }


def extractItemValue(item_html):
    label = item_html.find('h4')
    if label: 
        label.decompose()
    return (item_html.find('li').text if item_html.find('li') else item_html.text).strip()
        


def extractSampleParameters(document_soup):
    return {
        item.find('h4').text.strip() : extractItemValue(item)
        for item 
        in document_soup.find(
            'h3',
            string=lambda text: "Sample Parameters" in text
        ).parent.parent.find_all('li') 
        if item.find('h4')
    }


def extractProposalNumber(document_soup):
    item = document_soup.find(
        'h4',
        class_="details-name",
        string=lambda text: "Proposal number" in text
    ).parent
    item.find('h4').decompose()
    return item.text.strip()


def extractExperimentalReport(doi_url,document_soup):
    a_items = [item for item in document_soup.find_all("a",class_="btn-info") if 'Experimental Report' in item.text]
    return doi_url[:-1] + a_items[0].attrs['href'] if a_items else ""


def scrapeDocumentInformation(document_doi_url,doi_data_provider_url):

    res = requests.get(document_doi_url)

    document_soup = BeautifulSoup(res.content, "html.parser")

    data_url = doi_data_provider_url + [
        item 
        for item 
        in document_soup.find_all("a",class_="btn-info") 
        if 'Download Data' in item.text
    ][0].attrs['href']

    proposal_id = data_url.split('&')[-1].split("=")[-1]

    return {
        'documentDoiUrl': document_doi_url,
        'experimentalReportUrl': extractExperimentalReport(doi_data_provider_url,document_soup),
        'dataUrl': data_url,
        'proposalNumber' : extractProposalNumber(document_soup),
        'proposalId': proposal_id,
        'instruments': extractInstruments(document_soup),
        'metadata': {
            'authors' : extractAuthorsInfo(document_soup),
            'publicationYear' : extractPublicationYear(document_soup),
            'cycles' : extractCycles(document_soup),
            'experimentalParameters' : extractExperimentParameters(document_soup),
            'sampleParameters' : extractSampleParameters(document_soup)
        }
    }


# Loop on all the documents and retrieve the full record from ESS SciCat
print("Preparing raw data for task 1")
documents = []
errors = []
for document in panosc_documents:
    document_doi_url = doi_data_provider_url + document['doi']
    try:
        documents.append({
            'panosc':document,
            'document':scrapeDocumentInformation(document_doi_url,doi_data_provider_url)
        })
        print(".",end="",flush=True)
    except:
        print("+",end="",flush=True)
        errors.append(document_doi_url)
   
print("")
print("Raw data for task 1 preparation completed")

print("{} errors encountered".format(len(errors)))
for error in errors:
    print(" - " + error)


# Prepare data file name and save
output_data_file = "../data/oscars_pan_finder_ill_data_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
print("Saving raw data in file : " + output_data_file)
with open(output_data_file,'w') as fh:
    json.dump(documents,fh)


print("----------------------------------------------------------")
print(datetime.datetime.now().isoformat())
print("ILL data for OSCARS PaN-Finder project retrieved and saved")



