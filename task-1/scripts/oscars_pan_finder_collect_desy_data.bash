#!/usr/bin/bash
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Data collector for PaN-Finder:
# - DESY (Deutsches Elektronen-Synchrotron, https://desy.de)
#
# This script run the data collection script in the correct python environment.
#

micromamba run -n oscars-pan-finder-task-1 ./oscars_pan_finder_collect_desy_data.py

