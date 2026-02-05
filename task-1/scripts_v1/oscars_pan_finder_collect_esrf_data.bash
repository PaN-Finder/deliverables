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


