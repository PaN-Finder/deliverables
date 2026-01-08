#!/usr/bin/env python
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 v2 - Body of Knowledge
#
# Data collector for PaNOSC data provider:
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script run the data collection script in the correct python environment.
# This script leverage the ESRF data portal to collect additional information on each PaNOSC document.
# This new version interact directly with API endpoints and not the data portal frontend.
#
# Each document is saved in a separate file named:
#  ../data/esrf/esrf_document_<pid>.json
#
# Usage: oscars_pan_finder_collect_esrf_catalogue_data -d <doi of the document> -i <input file>
#
# - doi_of_the_document: the doi of the document that we want to collect all the information about
# - input_file: the file containing the information from the panosc portal. Optional.
#
# documents that already present in the folder are not downloaded
# 
# Version: 4.0
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

def get_config(data_portal_config_esrf_file: None):
    print("get_config - BEGIN")
    config = {}

    if data_portal_config_esrf_file is None:
        print("Config file not defined")
        data_portal_config_esrf_file = "../data/esrf/esrf_data_portal_config.json"
    data_portal_config_esrf_file = os.path.abspath(data_portal_config_esrf_file)

    print("Config file : ", data_portal_config_esrf_file)
    if not os.path.exists(data_portal_config_esrf_file):
        print("Get config from portal")
        print(f"Config url  : {settings.data_portal_config_url}")
        res = requests.get(settings.data_portal_config_url)
        print(" -- configuration request result : ", res.status_code)
        config = res.json()
        print(" -- saving configuration to file")
        with open(data_portal_config_esrf_file, "w") as f:
            json.dump(config,f)
    else:
        print("Loaded config from file")
        with open(data_portal_config_esrf_file) as f:
            config = json.load(f)

    print("get_config - END")
    return config


def get_session(user_info: dict):
    print("get_session - BEGIN")
    payload = settings.session_payload
    payload["username"] = user_info["username"]
    payload["password"] = user_info["password"]
    payload["plugin"] = user_info["plugin"]

    print("requesting session")
    res = requests.post(
        settings.session_url,
        json=payload,
    )
    print(" -- session request result : ", res.status_code)

    session_info = res.json()

    print(" -- session info : ", session_info)

    print("get_session - BEGIN")
    return session_info["sessionId"]


def retrieve_panosc_entry(doi, panosc_entry, panosc_input_file):
    print("get_panosc_entry - BEGIN")
    output_data = {}
    try:
        print("checking panosc entry")
        output_data = json.loads(panosc_entry);
        print("valid panosc entry")
    except:
        print("invalid panosc entry")
        try:
            print("loading panosc input file")
            with open(panosc_input_file) as f:
                panosc_data = json.load(f)
                output_data = [e for e in panosc_data if e["doi"] == doi][0]
            print("found panosc entry in file")
        except:
            print("impossible toi retrieve panosc entry from input file")

    print("get_panosc_entry - END")
    return output_data


def retrieve_datacite_info(doi):
    print("retrieve_datacite_info - BEGIN")
    if doi:
        try:
            datacite_url = re.sub("<DOI>",doi,settings.datacite_base_url)
            print(" -- datacite url : " + datacite_url)
            res = requests.get(datacite_url)
            print(" -- request result : ", res.status_code)
            output_data = res.json()
        except:
            print("impossible to retrieve datacite info")
            output_data ="Error retrieving resource"
    else:
        print ("doi not available")
        output_data = "Not doi available"

    print("retrieve_datacite_info - END")
    return output_data


def remove_fields(initem,fields):
    outitem = dict(initem)
    for field in fields:
        if field in outitem.keys():
            del outitem[field]
    return outitem


def extract_fields(initem,fields):
    delete_fields = set(initem.keys()).difference(set(fields))
    return remove_fields(initem,delete_fields)


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


def fix_sample_parameter(initem):
    outitem = dict(initem)
    del outitem["id"]
    return outitem


def fix_sample(initem):
    outitem = dict(initem)
    outitem = remove_fields(outitem,["investigation","meta","datasets"])
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


def retrieve_investigation(catalogue_url,pid):
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
    elif not pid:
        investigation_data = "Investigation id not provided"
    else:
        try:
            session_investigation_url = urllib.parse.urljoin(catalogue_url, "investigation")
            print(" -- session investigation Url : " + session_investigation_url)

            params = {
                "ids" : pid
            }

            res = requests.get(
                url = session_investigation_url,
                params = params
            )
            print(" -- request result : ", res.status_code)

            investigation_data = remove_fields(res.json()[0],["meta","type"])
        except:
            print(" -- error retrieving resource")
            investigation_data = "Error retrieving resource"

    print("retrieve_investigation - END")
    return investigation_data


def retrieve_datasets(catalogue_url, pid):
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
    elif not pid:
        print(" -- no pid")
        datasets_entries = "Investigation id not provided"
    else:
        try:
            session_datasets_url =  urllib.parse.urljoin(catalogue_url, "dataset")
            print(" -- session datasets url : " + session_datasets_url)

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


def retrieve_reports(doi):
    print("retrieve_reports - BEGIN")

    # curl - X
    # GET
    # "https://icatplus.esrf.fr/doi/10.15151/ESRF-ES-932918813/reports" - H
    # "accept: application/json"

    reports_entries = None
    try:
        reports_url = re.sub("<DOI>", doi, settings.reports_base_url)
        print(" -- reports url : " + reports_url)
        res = requests.get(reports_url)
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


def retrieve_users(catalogue_url,pid):
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
    elif not pid:
        print(" - no pid")
        users_entries = "Investigation pid not provided"
    else:
        try:
            session_users_url =  "/".join([catalogue_url, "investigation", "id", pid, "investigationusers"])
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
            **extract_fields(v,["fullName","email","familyName","givenName","affiliation"]),
            **{
                "orcid": v["orcidId"],
                "roles": list(v["roles"]),
            }
        }
        for k,v
        in temp.items()
    ]


def prepare_entry(
        panosc_entry,
        datacite_entry,
        investigation_entry,
        reports_entry,
        datasets_entries,
        samples_entries,
        users_entries,
):
    print("prepare_entry - BEGIN")
    if panosc_entry is None:
        panosc_entry = {}

    output = {
        "panosc" : panosc_entry,
        "datacite" : datacite_entry,
        "document" : investigation_entry,
        "datasets" : datasets_entries,
        "reports" : reports_entry,
        "samples" : samples_entries,
        "users" : users_entries,
    }

    print("retrieve_all_data - END")
    return output


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
        "-p","--pe","--panosc-entry",
        help="Panosc entry for this doi. Full entry as json string. It takes precedence over panosc input file",
        dest="panosc_entry",
        default="",
        type=str
    )
    parser.add_argument(
        "-i","--pif","--panosc-input-file",
        help="File containing the data collected from the PaNOSC data portal.",
        dest="panosc_input_file",
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
    panosc_entry = args.panosc_entry
    panosc_input_file = os.path.abspath(args.panosc_input_file) if args.panosc_input_file else ""
    conf_file = os.path.abspath(args.conf_file)
    include_samples = args.include_samples
    include_datafiles = args.include_datafiles
    include_users = args.include_users
    output_folder = os.path.abspath(args.output_folder)

    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_entry - BEGIN")
    print("Version 4.0")
    print(datetime.datetime.now().isoformat())
    print("----------------------------------------------------------")
    print("Input arguments:")
    print(" - Doi               : {}".format(doi))
    print(" - PaNOSC Entry      : {}".format(panosc_entry))
    print(" - PaNOSC Input file : {}".format(panosc_input_file))
    print(" - Portal Conf file  : {}".format(conf_file))
    print(" - Include samples   : {}".format(include_samples))
    print(" - Include datafiles : {}".format(include_datafiles))
    print(" - Include users     : {}".format(include_users))
    print(" - Output Folder     : {}".format(output_folder))
    print("")

    safe_doi = re.sub("[ /.-]", "_", doi)

    document_file = [f for f in os.listdir(output_folder) if safe_doi in f]
    if document_file:
        print(" - document already retrieved {}".format(document_file[0]))
    else:
        document_file =  output_folder + "/esrf_document_" + safe_doi + ".json"
        print(" - saving data in file: " + document_file)

        config = get_config(conf_file)
        sessionId = get_session(user_info = config["authentication"]["anonymous"])
        catalogue_url = re.sub("<SESSION_TOKEN>",sessionId,settings.catalogue_base_url)

        panosc_entry = retrieve_panosc_entry(doi, panosc_entry, panosc_input_file)
        pid = extract_pid(doi, panosc_entry)

        datacite_entry = retrieve_datacite_info(doi)
        investigation_entry = retrieve_investigation(catalogue_url, pid)

        release_date = get_release_date(datacite_entry)
        is_public = is_investigation_public(release_date)

        reports_entries = "Not public"
        datasets_entries = "Not public"
        samples_entries = "Not public"
        users_entries = "Not public"
        if is_public:
            reports_entries = retrieve_reports(doi)

            datasets_entries = retrieve_datasets(catalogue_url, pid)

            if include_samples:
                samples_entries = retrieve_samples(catalogue_url, pid)
            else:
                samples_entries = "Not included"

            if include_users:
                users_entries = retrieve_users(catalogue_url, pid)
            else:
                users_entries = "Not included"

            #if include_datafiles:
                #datafiles_entries = retrieve_datafiles(catalogue_url, pid)

        entry = prepare_entry(
            panosc_entry,
            datacite_entry,
            investigation_entry,
            reports_entries,
            datasets_entries,
            samples_entries,
            users_entries,
        )

        with open(document_file, 'w') as fh:
            json.dump(entry, fh)
    print("----------------------------------------------------------")
    print(datetime.datetime.now().isoformat())
    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_entry - END")



if __name__ == "__main__":
    main()
    exit(0)




        

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

