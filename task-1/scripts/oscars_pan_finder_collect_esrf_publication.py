#!/usr/bin/env python
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 v2 - Body of Knowledge
#
# Data collector for publications from PaN data provider :
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script run the data collection script in the correct python environment.
# This script leverage the ESRF data portal to collect the list of all public publications and additional information on each document.
# This version interacts directly with API endpoints accessible at https://icatplus.esrf.fr/api-docs/.
#
# Each document is saved in a separate file named:
#  ../data/esrf/esrf_document_<doi>.json
#
# Usage: oscars_pan_finder_collect_esrf_publications
#   -d, --doi : Doi of the document to be retrieved from ESRF data portal
#   -c, --portal-conf-file = Path to the file containing the configuration for the portal. It will be created if it does not exists. Default="../data/esrf/esrf_data_portal_config.json"
#   -s, --include-samples = Include samples information in entry
#   -f, --include-datafiles = Include datafiles information in entry
#   -u, --include-users = Include users information in entry
#   -o, --output-folder = Path to the folder where we will save the output file. Default=../data/esrf/
#
# documents that already present in the data folder are not downloaded
# 
# Version: 1.0
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


import requests
import json
import os
import urllib.parse
import datetime
import random
from bs4 import BeautifulSoup
import re
#from playwright.sync_api import sync_playwright, expect
from IPython.display import display, JSON
import sys
import argparse
import oscars_pan_finder_settings_esrf as settings

# def get_config(data_portal_config_esrf_file: None):
#     print("get_config - BEGIN")
#     config = {}
#
#     if data_portal_config_esrf_file is None:
#         print("Config file not defined")
#         data_portal_config_esrf_file = "../data/esrf/esrf_data_portal_config.json"
#     data_portal_config_esrf_file = os.path.abspath(data_portal_config_esrf_file)
#
#     print("Config file : ", data_portal_config_esrf_file)
#     if not os.path.exists(data_portal_config_esrf_file):
#         print("Get config from portal")
#         print(f"Config url  : {settings.data_portal_config_url}")
#         res = requests.get(settings.data_portal_config_url)
#         print(" -- configuration request result : ", res.status_code)
#         config = res.json()
#         print(" -- saving configuration to file")
#         with open(data_portal_config_esrf_file, "w") as f:
#             json.dump(config,f)
#     else:
#         print("Loaded config from file")
#         with open(data_portal_config_esrf_file) as f:
#             config = json.load(f)
#
#     print("get_config - END")
#     return config
#
#
# def get_session(user_info: dict):
#     print("get_session - BEGIN")
#     payload = settings.session_payload
#     payload["username"] = user_info["username"]
#     payload["password"] = user_info["password"]
#     payload["plugin"] = user_info["plugin"]
#
#     print("requesting session")
#     res = requests.post(
#         settings.session_url,
#         json=payload,
#     )
#     print(" -- session request result : ", res.status_code)
#
#     session_info = res.json()
#
#     print(" -- session info : ", session_info)
#
#     print("get_session - BEGIN")
#     return session_info["sessionId"]


# {
# 	"GET": {
# 		"scheme": "https",
# 		"host": "icatplus.esrf.fr",
# 		"filename": "/catalogue/a1a4c6c7-a77c-44cc-b06e-4cd9439c1dfd/datacollection",
# 		"query": {
# 			"datasetId": "2378104896"
# 		},
# 		"remote": {
# 			"Address": "193.49.43.164:443"
# 		}
# 	}
# }
#



# def retrieve_panosc_entry(doi, panosc_entry, panosc_input_file):
#     print("get_panosc_entry - BEGIN")
#     output_data = {}
#     try:
#         print("checking panosc entry")
#         output_data = json.loads(panosc_entry);
#         print("valid panosc entry")
#     except:
#         print("invalid panosc entry")
#         try:
#             print("loading panosc input file")
#             with open(panosc_input_file) as f:
#                 panosc_data = json.load(f)
#                 output_data = [e for e in panosc_data if e["doi"] == doi][0]
#             print("found panosc entry in file")
#         except:
#             print("impossible toi retrieve panosc entry from input file")
#
#     print("get_panosc_entry - END")
#     return output_data


# def remove_fields(initem,fields):
#     outitem = dict(initem)
#     for field in fields:
#         if field in outitem.keys():
#             del outitem[field]
#     return outitem
#
#
# def extract_fields(initem,fields):
#     delete_fields = set(initem.keys()).difference(set(fields))
#     return remove_fields(initem,delete_fields)


def fix_dataset_parameter(initem):
    outitem = dict(initem)
    del outitem["id"]
    del outitem["datasetId"]
    return outitem


def fix_dataset(initem):
    outitem = dict(initem)
    outitem = settings.remove_fields(outitem,["investigation","meta"])
    outitem["parameters"] = [fix_dataset_parameter(parameter) for parameter in outitem["parameters"]]
    return outitem


def fix_sample_parameter(initem):
    outitem = dict(initem)
    del outitem["id"]
    return outitem


def fix_sample(initem):
    outitem = dict(initem)
    outitem = settings.remove_fields(outitem,["investigation","meta","datasets"])
    outitem["parameters"] = [fix_sample_parameter(parameter) for parameter in outitem["parameters"]]
    return outitem


def extract_pid(doi, panosc_entry):
    print("extract_pid - BEGIN")
    if isinstance(panosc_entry,dict) and panosc_entry:
        pid = panosc_entry["pid"]
    else:
        pid = doi.split("-")[-1]
    print(" -- pid : {}".format(pid))
    print("extract_pid - END")
    return pid

def retrieve_doi_dataset(doi_url):
    """
    Collect dataset information from doi.

    Post a GET request to ESRF catalogue as follows:
    ```
    curl -X GET "https://icatplus.esrf.fr/doi/10.15151/ESRF-DC-2406973769/datasets" -H  "accept: application/json"
    {
	    "GET": {
		    "scheme": "https",
		    "host": "icatplus.esrf.fr",
		    "filename": "/doi/10.15151/ESRF-DC-2378105388/datasets",
		    "query": {
			    "limit": "20",
			    "skip": "0"
		    },
		    "remote": {
			    "Address": "193.49.43.164:443"
		    }
	    }
    }
    ```
    """
    print("retrieve_doi_datasets - BEGIN")

    doi_dataset_data = ""
    if not doi_url:
        doi_datasets_data = "Catalogue URL with Session not provided"
    else:
        try:
            doi_datasets_url = urllib.parse.urljoin(doi_url, "datasets")
            print(" -- doi datasets Url : " + doi_datasets_url)

            res = requests.get(
                url = doi_datasets_url,
                headers={"Accept": "application/json"},
            )
            print(" -- request result : ", res.status_code)

            doi_datasets_data = [
                settings.remove_fields(ds,["meta","type"])
                for ds
                in res.json()
            ]
        except:
            print(" -- error retrieving resource")
            doi_datasets_data = "Error retrieving resource"

    print("retrieve_doi_datasets - END")
    return doi_datasets_data

def retrieve_doi_datacite(doi_url):
    # {
    # 	"GET": {
    # 		"scheme": "https",
    # 		"host": "icatplus.esrf.fr",
    # 		"filename": "/doi/10.15151/ESRF-DC-2378105388/json-datacite",
    # 		"remote": {
    # 			"Address": "193.49.43.164:443"
    # 		}
    # 	}
    # }
    #
    print("retrieve_doi_datacite - BEGIN")

    doi_datacite_data = ""
    if not doi_url:
        doi_datacite_data = "DOI URL not provided"
    else:
        try:
            doi_datacite_url = urllib.parse.urljoin(doi_url, "json-datacite")
            print(" -- doi datacite Url : " + doi_datacite_url)

            res = requests.get(
                url = doi_datacite_url,
                #headers={"Accept": "application/json"},
            )
            print(" -- request result : ", res.status_code)

        except:
            print("impossible to retrieve datacite info")
            doi_datacite_data ="Error retrieving resource"

    print("retrieve_datacite_info - END")
    return doi_datacite_data


def retrieve_datacite_entry(datacite_url):
    #
    # {
    # 	"GET": {
    # 		"scheme": "https",
    # 		"host": "api.datacite.org",
    # 		"filename": "/dois/10.15151/ESRF-DC-2378105388",
    # 		"remote": {
    # 			"Address": "34.246.128.192:443"
    # 		}
    # 	}
    # }
    print("retrieve_datacite_entry - BEGIN")

    datacite_data = ""
    if not datacite_url:
        datacite_data = "Datacite URL not provided"
    else:
        try:
            print(" -- doi datacite Url : " + datacite_url)

            res = requests.get(
                url=datacite_url,
                headers={"Accept": "application/json"},
            )
            print(" -- request result : ", res.status_code)
            datacite_data = res.json()

        except:
            print("impossible to retrieve datacite entry")
            datacite_data = "Error retrieving resource"

    print("retrieve_datacite_info - END")
    return datacite_data

def retrieve_investigation(catalogue_url,investigation_id):
    """
    Collect more info regarding the investigation.

    Post a GET request to ESRF catalogue as follows:
    ```
    https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/investigation?ids=144479045
    ```
    """
    print("retrieve_investigation - BEGIN")

    investigation_data = ""
    if not catalogue_url:
        investigation_data = "Catalogue URL with Session not provided"
    elif not investigation_id:
        investigation_data = "Investigation id not provided"
    else:
        try:
            session_investigation_url = urllib.parse.urljoin(catalogue_url, "investigation")
            print(" -- session investigation Url : " + session_investigation_url)

            params = {
                "ids" : investigation_id
            }

            res = requests.get(
                url = session_investigation_url,
                params = params
            )
            print(" -- request result : ", res.status_code)

            investigation_data = settings.remove_fields(res.json()[0],["meta","type"])
        except:
            print(" -- error retrieving resource")
            investigation_data = "Error retrieving resource"

    print("retrieve_investigation - END")
    return investigation_data


def retrieve_datasets(catalogue_url, investigation_id):
    """
    Retrieve all the datasets associated with this document

    It does a GET request to ESRF catalogue as follow:
    ```
    https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/dataset?investigationIds=144479045&datasetType=acquisition&sortBy=STARTDATE&sortOrder=-1&nested=true&limit=20&skip=0
    ```
    """
    print("retrieve_dataset - BEGIN")
    datasets_entries = None

    if not catalogue_url:
        print(" -- no catalogue with session")
        datasets_entries = "Catalogue Url with Session not provided"
    elif not investigation_id:
        print(" -- no pid")
        datasets_entries = "Investigation id not provided"
    else:
        try:
            session_datasets_url =  urllib.parse.urljoin(catalogue_url, "dataset")
            print(" -- session datasets url : " + session_datasets_url)

            params = {
                "investigationIds" : investigation_id,
                "datasetType" : "acquisition",
                "sortBy" : "STARTDATE",
                "sortOrder" : -1,
                "nested" : True
            }

            res = requests.get(
                url = session_datasets_url,
                params = params
            )
            print(" -- request result status : ", res.status_code)
            datasets_entries = [fix_dataset(item) for item in res.json()]
        except:
            print(" -- error retrieving datasets")
            datasets_entries = "Error retrieving datasets"


    print("retrieve_dataset - END")
    return datasets_entries


def get_release_date(datacite_entry):
    return [e["date"] for e in datacite_entry["dates"] if e["dateType"] == "Available"][0]


def is_investigation_public(release_date):
    return datetime.datetime.strptime(release_date, "%Y-%m-%d") < datetime.datetime.now()


def retrieve_reports(doi_url):
    print("retrieve_reports - BEGIN")

    # curl - X
    # GET
    # "https://icatplus.esrf.fr/doi/10.15151/ESRF-ES-932918813/reports" - H
    # "accept: application/json"

    reports_entries = None
    doi_datacite_data = ""
    if not doi_url:
        doi_datacite_data = "DOI URL not provided"
    else:
        try:
            doi_reports_url = urllib.parse.urljoin(doi_url, "reports")
            print(" -- doi datacite Url : " + doi_reports_url)

            res = requests.get(doi_reports_url)
            print(" -- request result status: ", res.status_code)
            reports_data = res.json()

            reports_entries = [
                re.sub("<REPORT>",r, settings.sftp_reports_base)
                for e
                in reports_data
                for r
                in e["reports"]
            ]

        except:
            print("impossible to retrieve datacite info")
            reports_entries = "Error retrieving resource"

    print("retrieve_reports - END")
    return reports_entries


def retrieve_samples(catalogue_url,pid):
    """
    Retrieve all the samples associated with this document

    It does a GET request to ESRF catalogue as follow:
    ```
    https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/samples?investigationId=144479045&search=&limit=20
    ```
    """
    print("retrieve_samples - BEGIN")

    samples_entries = None
    if not catalogue_url:
        print(" - no catalogue url token")
        samples_entries = "Catalogue Url with Session not provided"
    elif not pid:
        print(" - no pid")
        samples_entries = "Investigation pid not provided"
    else:
        try:
            session_samples_url =  urllib.parse.urljoin(catalogue_url, "samples")
            print(" -- session samples url : " + session_samples_url)

            params = {
                "investigationId" : pid,
                "sortBy" : "NAME",
                "sortOrder" : 1,
            }

            res = requests.get(
                url = session_samples_url,
                    params = params
            )
            print(" -- request result status : ", res.status_code)

            samples_entries = [fix_sample(e) for e in res.json()]
        except:
            print(" -- error retrieving samples")
            samples_entries = "Error retrieving samples"

    print(" - retrieve_samples - END")
    return samples_entries


def retrieve_users(catalogue_url,investigation_id):
    """
    Retrieve all the users associated with this document

    It does a GET request to ESRF catalogue as follow:
    ```
    https://icatplus.esrf.fr/catalogue/9b5ff273-f1fe-4ab8-9627-17e870e53a5a/investigation/id/932918813/investigationusers
    ```
    """
    print("retrieve_users - BEGIN")

    users_entries = None
    if not catalogue_url:
        print(" - no catalogue url token")
        users_entries = "Catalogue Url with Session not provided"
    elif not investigation_id:
        print(" - no pid")
        users_entries = "Investigation pid not provided"
    else:
        try:
            session_users_url =  '/'.join([catalogue_url, "investigation", "id",str(investigation_id), "investigationusers"])
            print(" -- session users url : " + session_users_url)

            res = requests.get(
                url = session_users_url,
            )
            print(" -- request result status : ", res.status_code)

            users_entries = fix_users(res.json())
        except:
            print(" -- error retrieving users")
            users_entries = "Error retrieving users"

    print(" - retrieve_users - END")
    return users_entries

def fix_users(users):
    temp = {}
    for user in users:
        if user["name"] not in temp:
            temp[user["name"]] = user
            temp[user["name"]]["roles"] = set([user["role"]])
            del temp[user["name"]]["role"]
        else:
            temp[user["name"]]["roles"].add(user["role"])

    return [
        {
            **settings.extract_fields(v,["fullName","email","familyName","givenName","affiliation"]),
            **{
                "orcid": v["orcidId"],
                "roles": list(v["roles"]),
            }
        }
        for k,v
        in temp.items()
    ]

def retrieve_datafiles(catalogue_url, in_datasets):
    out_datasets = [
        {
            **ds,
            "datafiles" : retrieve_datafiles_for_dataset(
                catalogue_url,
                ds["id"]
            )
        }
        for ds
        in in_datasets
    ]
    return out_datasets


def retrieve_datafiles_for_dataset(catalogue_url,dataset_id):
    """
    Retrieve all the datafiles associated with this document and its datasets

    It does with a GET request to ESRF catalogue for each dataset as follow:
    ```
    https://icatplus.esrf.fr/catalogue/cc06fd64-2b10-4f77-a194-bda0552580fd/datafile?datasetId=514590601&limit=1
    {
	    "GET": {
    		"scheme": "https",
    		"host": "icatplus.esrf.fr",
    		"filename": "/catalogue/a1a4c6c7-a77c-44cc-b06e-4cd9439c1dfd/datafile",
    		"query": {
    			"datasetId": "2361356337",
    			"limit": "1000"
    		},
    		"remote": {
    			"Address": "193.49.43.164:443"
    		}
    	}
    }
    ```
    """
    print(" - retrieve_datafiles - BEGIN ")

    datafiles_entries = ""
    if not catalogue_url:
        print(" - no catalogue url token")
        datafiles_entries = "Catalogue Url with Session not provided"
    elif not dataset_id:
        print(" - no dtaaset id")
        datafiles_entries = "Dataset id not provided"
    else:
        try:
            datafiles_url =  urllib.parse.urljoin(catalogue_url, "datafile")
            print(" -- datafiles url : " + datafiles_url)

            datafiles_entries = []
            keep_going = True
            skip = settings.initial_skip
            while keep_going:
                params = {
                    "datasetId": dataset_id,
                    "skip": skip,
                    "limit": settings.batch_limit
                }
                res = requests.get(
                    datafiles_url,
                    params=params
                )
                current_batch = res.json()
                keep_going = len(current_batch) == settings.batch_limit
                datafiles_entries += current_batch
                print(".", end="")
                skip += len(current_batch)

            datafiles_entries = [
                settings.remove_fields(
                    e['Datafile'],
                    ["dataset", "dataCollectionDatafiles", "destDatafiles","sourceDatafiles"]
                )
                for e
                in datafiles_entries
            ]

        except:
            print(" -- error retrieving data files")
            datafiles_entries = "Error retrieving data files"

    print(" - retrieve_datafiles - END")
    return datafiles_entries

def fix_datafiles(datafiles_entries):
    return settings.extract_fields(
        datafiles_entries['Datafile'],
        ["id","createTime","modTime","fileSize","location","name","isReleased"])

def retrieve_data_collection(catalogue_url, dataset_doi):
    # curl -X GET
    # "https://icatplus.esrf.fr/catalogue/fb87a66f-54e9-4b6b-a265-8320ac266f7d/datacollection?datasetId=2322952068" -H  "accept: application/json"
    # curl
    # - X GET
    # "https://icatplus.esrf.fr/catalogue/fb87a66f-54e9-4b6b-a265-8320ac266f7d/datacollection?search=10.15151%2FESRF-DC-2406973769"
    # - H "accept: application/json"
    print(" - retrieve_data_collection - BEGIN ")

    data_collection_entry = ""
    if not catalogue_url:
        print(" - no catalogue url token")
        data_collection_entry = "Catalogue Url with Session not provided"
    elif not dataset_doi:
        print(" - no dataset id")
        data_collection_entry = "dataset id not provided"
    else:
        try:
            data_collection_url =  urllib.parse.urljoin(catalogue_url, "datacollection")
            print(" -- data collection url : " + data_collection_url)

            params = {
                "datasetID": dataset_doi
            }

            res = requests.get(
                data_collection_url,
                params=params,
                headers={"Accept": "application/json"}
            )

            data_collection_entries = res.json()
            print(f" - retrieved {len(data_collection_entries)} data collection entries")
            data_collection_entry = settings.extract_fields(
                data_collection_entries[0],
                ["createTime", "modTime", "dataCollectionDatasets", "doi", "parameters"]
            )

        except:
            print(" -- error retrieving data collection")
            data_collection_entry = "Error retrieving data collection"

    print(" - retrieve_data_collection - END")
    return data_collection_entry



def prepare_entry(
            pub_entry,
            doi_datacite_entry,
            datacite_entry,
            reports_entries,
            doi_datasets_entries,
            samples_entries,
            users_entries,
            citation_entries,
            instruments_entries,
            investigation_entries
):
    print("prepare_entry - BEGIN")

    output = {
        "panosc" : {},
        "datacite" : [
            datacite_entry,
            doi_datacite_entry,
        ],
        "collection" : pub_entry,
        "datasets" : doi_datasets_entries,
        "reports" : reports_entries,
        "samples" : samples_entries,
        "users" : users_entries,
        "citations" : citation_entries,
        "instruments" : instruments_entries,
        "investigation" : investigation_entries
    }

    print("retrieve_all_data - END")
    return output

def extract_investigations_from_datasets(doi_datasets_entries):
    investigations = {
        i["investigation"]["id"]: i["investigation"]
        for i
        in doi_datasets_entries
    }
    investigations = [
        i for i in investigations.values()
    ]
    return investigations

def extract_instruments_from_investigations(investigation_entries):
    instruments = {
        rec['instrument']["id"]: rec['instrument']
        for inv
        in investigation_entries
        for rec
        in inv["investigationInstruments"]
    }
    instruments = [
        settings.remove_fields(
            i,
            ["shifts","datasetInstruments","instrumentScientists","investigationInstruments"]
        )
        for i
        in instruments.values()
    ]
    return instruments

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d","--doi",
        help="Doi of the document to be retrieved from ESRF data portal",
        dest="doi",
        required=True,
        type=str
    )
    parser.add_argument(
        "-p","--pe","--publication-entry",
        help="Publication entry for this doi. Full entry as json string.",
        dest="pub_entry",
        default="",
        type=str
    )
    parser.add_argument(
        "-c","--portal-conf-file",
        help="Path to the file containing the configuration for the portal. It will be created if it does not exists.",
        dest="conf_file",
        default="../data/esrf/esrf_data_portal_config.json",
        type=str
    )
    parser.add_argument(
        "-s", "--include-samples",
        help="Include samples information in entry",
        dest="include_samples",
        action="store_true",
    )
    parser.add_argument(
        "-f", "--include-datafiles",
        help="Include datafiles information in entry",
        dest="include_datafiles",
        action="store_true",
    )
    parser.add_argument(
        "-u", "--include-users",
        help="Include users information in entry",
        dest="include_users",
        action="store_true",
    )
    parser.add_argument(
        "-o","--output-folder",
        help="Path to the folder where we will save the output file.",
        dest="output_folder",
        default="../data/esrf/",
        type=str
    )


    args = parser.parse_args()
    # transfer input to internal variables
    doi=args.doi
    pub_entry = args.pub_entry
    conf_file = os.path.abspath(args.conf_file)
    include_samples = args.include_samples
    include_datafiles = args.include_datafiles
    include_users = args.include_users
    output_folder = os.path.abspath(args.output_folder)

    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_publication - BEGIN")
    print("Version 1.0")
    print(datetime.datetime.now().isoformat())
    print("----------------------------------------------------------")
    print("Input arguments:")
    print(f" - Doi               : {format(doi)}")
    print(f" - Publication entry : {format(pub_entry)}")
    print(f" - Portal Conf file  : {format(conf_file)}")
    print(f" - Include samples   : {format(include_samples)}")
    print(f" - Include datafiles : {format(include_datafiles)}")
    print(f" - Include users     : {format(include_users)}")
    print(f" - Output Folder     : {format(output_folder)}")
    print("")

    safe_doi = re.sub("[ /.-]", "_", doi)

    document_file = [f for f in os.listdir(output_folder) if safe_doi in f]
    if document_file:
        print(" - document already retrieved {}".format(document_file[0]))
    else:
        document_file =  output_folder + "/esrf_publication_" + safe_doi + ".json"
        print(" - saving data in file: " + document_file)

        print("Retrieving session - BEGIN")
        config = settings.get_config(conf_file)
        session_id = settings.get_session(user_info = config["authentication"]["anonymous"])
        print(f" - Session Id                     : {session_id}")
        print("Retrieving session - END")

        print("Settings URL - BEGIN")
        catalogue_url = re.sub("<SESSION_TOKEN>", session_id, settings.catalogue_base_url)
        print(f" - Catalogue URL                  : {catalogue_url}")
        doi_url = re.sub("<DOI>", doi, settings.data_portal_doi_base_url)
        print(f" - DOI URL                        : {doi_url}")
        datacite_url = re.sub("<DOI>", doi, settings.datacite_base_url)
        print(f" - Datacite URL                   : {datacite_url}")
        print("Settings URL - END")

        doi_datacite_entry = retrieve_doi_datacite(doi_url)
        datacite_entry = retrieve_datacite_entry(datacite_url)
        doi_datasets_entries = retrieve_doi_dataset(doi_url)
        if not pub_entry:
            pub_entry = retrieve_data_collection(catalogue_url, doi_datasets_entries[0]["id"])

        # investigation_ids = list(set([
        #     ds["investigation"]["id"]
        #     for ds
        #     in doi_datasets_entries
        # ]))
        # print(f" - Investigation IDs : {investigation_ids}")
        # print(f" - Number of investigations : {len(investigation_ids)}")
        # investigation_id = investigation_ids[0]
        # print(f" - Selecting Investigation ID : {investigation_id}")

        #investigation_entry = retrieve_investigation(catalogue_url, investigation_id)
        investigation_entries = extract_investigations_from_datasets(doi_datasets_entries)
        doi_datasets_entries = [
            settings.remove_fields(
                ds,
                ["investigation"]
            )
            for ds in doi_datasets_entries
        ]
        investigation_ids = [
            i['id']
            for i
            in investigation_entries
        ]

        #release_date = get_release_date(datacite_entry)
        #is_public = is_investigation_public(release_date)

        reports_entries = retrieve_reports(doi_url)

        #datasets_entries = retrieve_datasets(catalogue_url, investigation_id)

        samples_entries = []
        users_entries = []
        for investigation_id in investigation_ids:
            if include_samples:
                entries = retrieve_samples(catalogue_url, investigation_id)
                if isinstance(entries, list):
                    samples_entries += entries
            if include_users:
                entries = retrieve_users(catalogue_url, investigation_id)
                if isinstance(entries, list):
                    users_entries += entries

        samples_entries = "Not included" if not include_samples else samples_entries
        users_entries = "Not included" if not include_users else users_entries

        citation_entries = ""

        instruments_entries = extract_instruments_from_investigations(investigation_entries)
        investigation_entries = [
            settings.remove_fields(
                i,
                ["investigationInstruments"]
            )
            for i in investigation_entries
        ]

        if include_datafiles:
            doi_datasets_entries = retrieve_datafiles(catalogue_url, doi_datasets_entries)

        entry = prepare_entry(
            pub_entry,
            doi_datacite_entry,
            datacite_entry,
            reports_entries,
            doi_datasets_entries,
            samples_entries,
            users_entries,
            citation_entries,
            instruments_entries,
            investigation_entries
        )

        with open(document_file, 'w') as fh:
            json.dump(entry, fh)
    print("----------------------------------------------------------")
    print(datetime.datetime.now().isoformat())
    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_entry - END")



if __name__ == "__main__":
    main()
    exit(0)

