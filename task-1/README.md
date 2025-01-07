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

     

### Setup

In order to run the data collection scripts, users are required to set up the proper environment.
The environment requires the following application and it has been tested on Linux machine (Specifically Ubuntu distribution)
- bash terminal
- mamba or micromamba package management (https://mamba.readthedocs.io/en/latest/index.html)
- jq cli (https://jqlang.github.io/jq/)

Following are instructions on how to properly set up the working environment:
- open a bask terminal
- install mamba or micromamba.
  For this example, we will install micromamba following the official instructions: https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html
  ```
  > "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
  100  3059  100  3059    0     0   5901      0 --:--:-- --:--:-- --:--:-- 11287
  Micromamba binary folder? [~/.local/bin] 
  Init shell (bash)? [Y/n]  
  Configure conda-forge? [Y/n] 
  Prefix location? [~/micromamba] 
  Running `shell init`, which:
   - modifies RC file: "/home/maxnovelli/.bashrc"
   - generates config for root prefix: "/home/maxnovelli/micromamba"
   - sets mamba executable to: "/home/maxnovelli/.local/bin/micromamba"
  The following has been added in your "/home/maxnovelli/.bashrc" file

  # >>> mamba initialize >>>
  # !! Contents within this block are managed by 'micromamba shell init' !!
  export MAMBA_EXE='/home/maxnovelli/.local/bin/micromamba';
  export MAMBA_ROOT_PREFIX='/home/maxnovelli/micromamba';
  __mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
  if [ $? -eq 0 ]; then
      eval "$__mamba_setup"
  else
      alias micromamba="$MAMBA_EXE"  # Fallback on help from micromamba activate
  fi
  unset __mamba_setup
  # <<< mamba initialize <<<

  Please restart your shell to activate micromamba or run the following:\n
  source ~/.bashrc (or ~/.zshrc, ~/.xonshrc, ~/.config/fish/config.fish, ...)

  ```
- create the mamba environment _named oscars-pan-finder-task-1_ weith the correct python version and libraries
  ```
  > micromamba create -n oscars-pan-finder-task-1 -f oscars-pan-finder-environment.yaml -c conda-forge
  ```

- install _jq_ program
  ```
  > sudo apt install jq
  ```

### Collect data

Cd into the scripts folder for task 1 and run in order all the data acquisition shell scripts.


First of all activate the python environment:
```
> 
micromamba activate oscars-pan-finder-task-1
micromamba run -n oscars-pan-finder-task-1 mycommand
```
