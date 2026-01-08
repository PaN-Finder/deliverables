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
# - ESRF (European Synchrotron Radiation Facility, https://www.esrf.fr/)
#
# This script use a previously collected list of PaNOSC entries to collect each individual entries from the ESRF data api
# We load the json file with all the ESRF PaNOSC entries and then loop through it to run the collection script
#  ../data/esrf/oscars_pan_finder_esrf_panosc_documents.json
#
# 
# Version: 1.0
#
#
import subprocess

import json
import os
import datetime
import argparse

import oscars_pan_finder_settings_esrf as settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i","--input-file",
        help="Name of the file containing the list of PaNOSC entries",
        dest="input_file",
        default="../data/esrf/oscars_pan_finder_esrf_panosc_documents.json",
        type=str
    )
    parser.add_argument(
        "-o","--output-folder",
        help="Path to the folder where we will save the output file.",
        dest="output_folder",
        default="../data/esrf/",
        type=str
    )
    args = parser.parse_args()
    input_file = os.path.abspath(args.input_file)
    output_folder = os.path.abspath(args.output_folder)

    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_entries_from_panosc_list - BEGIN")
    print("Version 4.0")
    print(datetime.datetime.now().isoformat())
    print("----------------------------------------------------------")

    print("Urls used to retrieve data");
    print(f" - ESRF Data Portal API Url   : {settings.panosc_data_provider_url}")
    print(f" - Input File                 : {input_file}")
    print(f" - Output Folder              : {output_folder}")


    print("Loading file with PaNOSC entries")
    with open(input_file, "r") as f:
        panosc_entries = json.load(f)
    print("File with PaNOSC entries loaded")
    print(f"Loaded {len(panosc_entries)} entries")


    print("Collection loop started")
    for entry in panosc_entries:
        print(f"Collecting {entry['doi']}")
        if isinstance(entry["doi"],str) and entry["doi"]:
            print("BEGIN ============")
            subprocess.run([
                "python",
                os.path.abspath("./oscars_pan_finder_collect_esrf_entry.py"),
                "-d",
                entry["doi"],
                "-p",
                json.dumps(entry),
                "-s",
                "-u"]
            )
            print("END ==============")
        else:
            print(f"No doi. Skipping entry {entry}")

    print("Collection loop completed")

    print("----------------------------------------------------------")
    print(datetime.datetime.now().isoformat())
    print("OSCARS PaN-Finder project - Task 1 - ESRF - oscars_pan_finder_collect_esrf_entries_from_panosc_list - END")


if __name__ == "__main__":
    main()
