#!/usr/bin/env bash
# coding: utf-8
#
#
# OSCARS project - https://oscars-project.eu/
# PaN-Finder     - https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder
# 
# Task 1 - Body of Knowledge
#
# Environment setup for ubuntu machines
#
# This script installs all the necessary packages and software to set up the environment to run the OSCARS PaN-Finder data collection.
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

# install micromamba software
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)

# creates the python environment needed for the data collection scripts
micromamba create -n oscars-pan-finder-task-1 -f ../oscars-pan-finder-environment.yaml -c conda-forge

# install software packages from official os distribution needed for working with json files
# and to run the data collections
sudo apt install -y jq ffmpeg libavif13 libgstreamer-plugins-bad1.0-0

# install the python package to load webpages and explore them
micromamba install playwright-python

# initialize the python package
micromamba run -n oscars-pan-finder-task-1 playwright install

