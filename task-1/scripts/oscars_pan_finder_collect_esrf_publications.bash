#!/usr/bin/bash
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Data collector for publications of PaN data provider:
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script run the data collection scripts in the correct order and correct python environment.
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
  echo "Removing all publications entries."
  rm -fv ${TEMP_DATA_FOLDER}/esrf_publication_*.json
else
  echo "Creating temp data folder"
  mkdir ${TEMP_DATA_FOLDER}
  ls ${TEMP_DATA_FOLDER}
fi

# collect ESRF list of publications
PUBLICATIONS_FILE=${TEMP_DATA_FOLDER}/oscars_pan_finder_esrf_publications.json
PUBLICATIONS_LIST_LOG=${TEMP_DATA_FOLDER}/oscars_pan_finder_esrf_publications_list.`date '+%Y%m%d%H%M%S%N'`.log
echo "Full list of publications file: ${PUBLICATIONS_FILE}"
echo "Publications list logs: ${PUBLICATIONS_LIST_LOG}"
micromamba run -n oscars-pan-finder-task-1 ./oscars_pan_finder_collect_esrf_publications.py -o ${PUBLICATIONS_FILE} 1>${PUBLICATIONS_LIST_LOG} 2>&1

# collect all ESRF publications
PUBLICATION_ENTRIES_LOG=${TEMP_DATA_FOLDER}/oscars_pan_finder_esrf_publications_entries.`date '+%Y%m%d%H%M%S%N'`.log
echo "Publications entries logs: ${PUBLICATIONS_ENTRIES_LOG}"
micromamba run -n oscars-pan-finder-task-1 ./oscars_pan_finder_collect_esrf_publications_from_file.py -i ${PUBLICATIONS_FILE} 1>${PUBLICATIONS_ENTRIES_LOG} 2>&1


# merge all the files
OUTPUT_FILE = "../data/oscars_pan_finder_esrf_publications_`date '+%Y%m%d%H%M%S%N'`.json"
jq -s '.' ../data/esrf/esrf_document_* >  ${output_file}
jq -c -s '.' ${TEMP_DATA_FOLDER}/esrf_publication_*.json > ${OUTPUT_DATA}


# compress file
zip ${OUTPUT_DATA}.zip ${OUTPUT_DATA}

