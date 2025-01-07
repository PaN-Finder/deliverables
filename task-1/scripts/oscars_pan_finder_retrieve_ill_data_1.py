#!/usr/bin/env python
# coding: utf-8

# # OSCARS PaN-Finder
# ## Retrieve all publicly accessible and published data from data provider: ILL
# 
# Data is retrieved from PaNOSC search interface and also from ILL doi portal
# 
# Version: 1.0

# In[1]:


import requests
import json
import os
import urllib.parse
import datetime
import random
from bs4 import BeautifulSoup
import re


# In[2]:


data_provider_url = "https://fairdata.ill.fr/fairdata/api/"
data_provider_url


# In[3]:


doi_url = "https://doi.ill.fr/"
doi_url


# In[4]:


initial_skip = 0
batch_limit = 1000


# PaNOSC search API  endpoints to retrieve documents and datasets

# In[5]:


document_url = urllib.parse.urljoin(data_provider_url + "/", "documents")
count_document_url = urllib.parse.urljoin(document_url + "/", "count")
dataset_url = urllib.parse.urljoin(data_provider_url + "/", "datasets")

print("SciCat urls");
print(f" - Published Data       : {document_url}")
print(f" - Published Data Count : {count_document_url}")
print(f" - Dataset              : {dataset_url}")


# In[6]:


res = requests.get(count_document_url)


# In[7]:


res.json()


# In[8]:


raw_documents = []
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
        document_url,
        params = params
    )
    current_batch = res.json()
    keep_going = len(current_batch) == batch_limit
    raw_documents += current_batch
    #print(f"Skip : {skip}. Params: {params}. Status Code: {res.status_code}. Url: {res.request.url}. Number of results: {len(current_batch)}. Continue: {keep_going}. Total number of datasets retrieved: {len(raw_documents)}")
    print(".",end="")
    skip += len(current_batch)
    #if skip > 21:
    #    break


# In[9]:


len(raw_documents)


# In[10]:


t1 = random.choice(raw_documents)


# In[11]:


t1


# In[12]:


t1['doi']


# In[13]:


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
        


# In[14]:


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


# In[15]:


def extractPublicationYear(document_soup):
    return document_soup.find(
        'h4',
        class_="details-name",
        string=lambda text: "Publication year" in text
    ).parent.text.strip().split(' ')[-1]


# In[16]:


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


# In[124]:


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


# In[54]:


def extractExperimentParameters(document_soup):
    return {
        item.find('h4').text.strip() : item.find('div').text.strip().split(' ')[-1]
        for item 
        in document_soup.find(
            'h3',
            string=lambda text: "Experiment Parameters" in text
        ).parent.parent.find_all('li')
    }


# In[88]:


def extractItemValue(item_html):
    label = item_html.find('h4')
    if label: 
        label.decompose()
    return (item_html.find('li').text if item_html.find('li') else item_html.text).strip()
        


# In[99]:


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


# In[132]:


def extractProposalNumber(document_soup):
    item = document_soup.find(
        'h4',
        class_="details-name",
        string=lambda text: "Proposal number" in text
    ).parent
    item.find('h4').decompose()
    return item.text.strip()


# In[156]:


def extractExperimentalReport(doi_url,document_soup):
    a_items = [item for item in document_soup.find_all("a",class_="btn-info") if 'Experimental Report' in item.text]
    return doi_url[:-1] + a_items[0].attrs['href'] if a_items else ""


# In[157]:


def scrapeDocumentInformation(doi):
    document_doi_url = doi_url + doi

    res = requests.get(document_doi_url)
    #print(res.content)

    document_soup = BeautifulSoup(res.content, "html.parser")

    data_url = doi_url + [
        item 
        for item 
        in document_soup.find_all("a",class_="btn-info") 
        if 'Download Data' in item.text
    ][0].attrs['href']

    proposal_number = ""

    proposal_id = data_url.split('&')[-1].split("=")[-1]

    return {
        'documentDoiUrl': document_doi_url,
        'experimentalReportUrl': extractExperimentalReport(doi_url,document_soup),
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


# In[159]:


documents = []
for raw_document in raw_documents:
    try:
        documents.append({
            'panosc':raw_document,
            'document':scrapeDocumentInformation(raw_document['doi'])
        })
        print(".",end="")
    except:
        print("\n" + raw_document['doi'])
    


# In[160]:


data_file_name = "../data/ill_open_data_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
data_file_name


# In[161]:


with open(data_file_name,'w') as fh:
    json.dump(documents,fh)


# In[ ]:




