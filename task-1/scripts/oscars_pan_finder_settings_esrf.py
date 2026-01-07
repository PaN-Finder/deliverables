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
# This script contains all the settings needed to interact with ESRF portal
#
# Version: 1.0
#

# PaNOSC API url
panosc_data_provider_url = "https://icatplus.esrf.fr/api"
panosc_documents_url = "https://icatplus.esrf.fr/api/Documents"
panosc_documents_count_url = "https://icatplus.esrf.fr/api/Documents/count"

# Parameters to batch load all the public documents available
initial_skip = 0
batch_limit = 1000

# ESRF Data Portal frontend
data_portal_frontend_url = "https://data.esrf.fr"

# ESRF Data Portal API Base
data_portal_api_base_url = "https://icatplus.esrf.fr"

# config file
data_portal_config_url = "https://icatplus.esrf.fr/config/api.config.json"

# Prepare all the endpoints needed to retrieve entries
datacite_base_url = "https://icatplus.esrf.fr/doi/<DOI>/json-datacite"
reports_base_url = "https://icatplus.esrf.fr/doi/<DOI>/reports"
session_url = "https://icatplus.esrf.fr/session"
catalogue_base_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/"
#catalogue_investigation_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/investigation"
#catalogue_dataset_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/dataset"
#catalogue_sample_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/samples"
#catalogue_datafile_url = "https://icatplus.esrf.fr/catalogue/<SESSION_TOKEN>/datafile"

sftp_reports_base = "http://ftp.esrf.fr/pub/UserReports/<REPORT>"

session_payload = {
  "plugin": "<PLUGIN>",
  "username": "<USERNAME>",
  "password": "<PASSWORD>"
}