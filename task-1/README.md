# Task 1
# Body of Knowledge

## [OSCARS project](https://oscars-project.eu/)
## [PaN-Finder](https://oscars-project.eu/projects/pan-finder-photon-and-neutron-federated-knowledge-finder)
#### Photon and Neutron federated knowledge finder

In this task, all available PaN knowledge will be harvested and the body of knowledge will be curated to be utilized for task 2. A series of python scripts will be created to retrieve all the entries available through the PaNOSC Data Portal and enrich them with linked resources such as institution data catalog entries and related publications.  
The body of knowledge will be finalized from the data collected by organizing it in a machine readable format, like json.  

The deliverables for this task are:
1.a. A repository with one or more files containing the body of knowledge in the selected format
     Folder _data_ contains all the data files collected with the script from deliverable 1.b and used in task 2.
     The folder provides one file for each facility used as data sources. The data files are in json format in raw format as retrieved by the matching script.
    
1.b. A code repository with all the scripts used to collect data and create the body of knowledge
     Folder _scripts_ contains all the scripts used to collect the data. There is one script for each facility selected as data source.
     Each script assumes that is run from the folder where is saved and will save the output in the _data_ folder provided in deliverable *1.a*

     



