#!/usr/bin/bash
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Data collector for PaNOSC data provider:
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script run the data collection scripts in the correct order and correct python environment.
#

# check if folder for temporary files is present
TEMP_DATA_FOLDER="../data/esrf"
if [ -d ${TEMP_DATA_FOLDER} ]; then
  echo "Directory ${TEMP_DATA_FOLDER} exists."
else
  echo "Creating temp data folder"
  mkdir ${TEMP_DATA_FOLDER}
  ls ${TEMP_DATA_FOLDER}
fi

# collect PaNOSC documents
micromamba run -n oscars-pan-finder-task-1 ./oscars_pan_finder_collect_esrf_panosc_documents.py

# collect Data catalogue information
micromamba run -n oscars-pan-finder-task-1 ./oscars_pan_finder_collect_esrf_catalogue_data.py ../data/esrf/oscars_pan_finder_esrf_panosc_documents.json -1

# merge all the files
output_file = "../data/oscars_pan_finder_esrf_data_`date '+%Y%m%d%H%M%S%N' | cut -b-20`.json"
jq -s '.' ../data/esrf/esrf_document_* >  ${output_file}


