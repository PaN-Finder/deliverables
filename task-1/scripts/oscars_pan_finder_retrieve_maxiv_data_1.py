#!/usr/bin/env python
# coding: utf-8

# # OSCARS PaN-Finder
# ## Retrieve all publicly accessible and published data from data provider: MaxIV
# 
# All data is directly retrieved from MaxIV SciCat instance

# In[1]:


import requests
import json
import os
import urllib.parse
import datetime
import random


# Instance settings

# In[2]:


data_provider_url = "https://scicat.maxiv.lu.se/api/v3/"
data_provider_url


# In[3]:


initial_skip = 0
batch_limit = 1000


# In[4]:


fields_to_be_deleted_from_document = ["thumbnail","history"]


# SciCat endpoints to retrieve published data and datasets

# In[5]:


publisheddata_url = urllib.parse.urljoin(data_provider_url + "/", "publisheddata")
count_publisheddata_url = urllib.parse.urljoin(publisheddata_url + "/", "count")
dataset_url = urllib.parse.urljoin(data_provider_url + "/", "datasets")

print("SciCat urls");
print(f" - Published Data       : {publisheddata_url}")
print(f" - Published Data Count : {count_publisheddata_url}")
print(f" - Dataset              : {dataset_url}")


# Load all publicly available data  
# (aka documents in PaNOSC terms, aka publishedData entities in SciCat terms),

# In[6]:


res = requests.get(count_publisheddata_url)


# In[7]:


res.json()


# In[8]:


raw_documents = []
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
        publisheddata_url,
        params = params
    )
    current_batch = res.json()
    #print(current_batch)
    keep_going = len(current_batch) == batch_limit
    raw_documents += current_batch
    #print(f"Skip : {skip}. Params: {params}. Status Code: {res.status_code}. Url: {res.request.url}. Number of results: {len(current_batch)}. Continue: {keep_going}. Total number of datasets retrieved: {len(datasets)}")
    print(".",end="")
    skip += len(current_batch)
    #if skip > 21:
    #    break


# Confirm that we retrieved the correct amount of documents

# In[9]:


len(raw_documents)


# Explore one entry, in order to visually verify

# In[10]:


random.choice(raw_documents)


# Functions to retrieve individual datasets from published data record

# In[15]:


def get_dataset(pid):
    res = requests.get(
        dataset_url + "/" + urllib.parse.quote_plus(pid)
    )
    return res.json()


# In[16]:


def get_datasets(pids):
    return [
        get_dataset(pid)
        for pid
        in pids
    ]


# Loop on all the documents and retrieve the full record from ESS SciCat

# In[17]:


documents = []


# In[18]:


for raw_document in raw_documents:
    for field_to_be_deleted in list(set(raw_document.keys()).intersection(fields_to_be_deleted_from_document)):
        raw_document.pop(field_to_be_deleted)
    documents.append({
        "document" : raw_document,
        "datasets" : get_datasets(raw_document['pidArray'])
    })
    print(".",end="")


# Verify the number of documents

# In[19]:


len(documents)


# Visually inspect one document

# In[20]:


random.choice(documents)


# Prepare data file name and save

# In[21]:


data_file_name = "../data/maxiv_open_data_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
data_file_name


# In[22]:


with open(data_file_name,'w') as fh:
    json.dump(documents,fh)


# In[ ]:





# In[ ]:





# In[ ]:




