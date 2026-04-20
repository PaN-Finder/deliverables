#!/usr/bin/env python
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
#
# Task 1 v2 - Body of Knowledge
#
# Data collector for PaN data provider:
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script contains all the settings needed to interact with ESRF portal
#
# Version: 1.1
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
import json
import os

import requests

# PaNOSC API url
panosc_data_provider_url = "https://icatplus.esrf.fr/api"
panosc_documents_url = "https://icatplus.esrf.fr/api/Documents"
panosc_documents_count_url = "https://icatplus.esrf.fr/api/Documents/count"

# Parameters to batch load all the public documents available
initial_skip = 0
batch_limit = 100

# ESRF Data Portal frontend
data_portal_frontend_url = "https://data.esrf.fr"

# ESRF Data Portal API Base
data_portal_api_base_url = "https://icatplus.esrf.fr"

# config file
data_portal_config_url = "https://data.esrf.fr/config/api.config.json"

# Prepare all the endpoints needed to retrieve entries
data_portal_doi_base_url = "https://icatplus.esrf.fr/doi/<DOI>/"
#doi_datasets_base_url = "https://icatplus.esrf.fr/doi/<DOI>/datasets"
#doi_datacite_base_url = "https://icatplus.esrf.fr/doi/<DOI>/json-datacite"
#doi_reports_base_url = "https://icatplus.esrf.fr/doi/<DOI>/reports"
session_url = "https://icatplus.esrf.fr/session"
catalogue_base_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/"
#catalogue_investigation_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/investigation"
#catalogue_dataset_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/dataset"
#catalogue_sample_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/samples"
#catalogue_datafile_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/datafile"
datacite_base_url = "https://api.datacite.org/dois/<DOI>"

sftp_reports_base = "http://ftp.esrf.fr/pub/UserReports/<REPORT>"

session_payload = {
  "plugin": "<PLUGIN>",
  "username": "<USERNAME>",
  "password": "<PASSWORD>"
}


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
    print(f"Config url  : {data_portal_config_url}")
    res = requests.get(data_portal_config_url)
    print(" -- configuration request result : ", res.status_code)
    config = res.json()
    print(" -- saving configuration to file")
    with open(data_portal_config_esrf_file, "w") as f:
      json.dump(config, f)
  else:
    print("Loaded config from file")
    with open(data_portal_config_esrf_file) as f:
      config = json.load(f)

  print("get_config - END")
  return config


def get_session(user_info: dict):
  print("get_session - BEGIN")
  payload = session_payload
  payload["username"] = user_info["username"]
  payload["password"] = user_info["password"]
  payload["plugin"] = user_info["plugin"]

  print("requesting session")
  res = requests.post(
    session_url,
    json=payload,
  )
  print(" -- session request result : ", res.status_code)

  session_info = res.json()

  print(" -- session info : ", session_info)

  print("get_session - BEGIN")
  return session_info["sessionId"]

def remove_fields(initem, fields):
  outitem = dict(initem)
  for field in fields:
    if field in outitem.keys():
      del outitem[field]
  return outitem

def extract_fields(initem, fields):
  delete_fields = set(initem.keys()).difference(set(fields))
  return remove_fields(initem, delete_fields)
