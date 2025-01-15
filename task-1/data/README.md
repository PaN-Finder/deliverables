# Data folder

This folder contains the data files with the data retrieved from the selected PaNOSC data provider.

## Files

The files in this folder contains the data/information collected from the relevant facilities.
THe name format is as follow:

- oscars_pan_finder_<facility_name>_data_<timestamp>.json[.zip]

where:
- facility_name is the acronym of the facility from where the data in the file has been collected from
- timestamp is the date and time of when the file has been collected and is formatted as %YYYY%mm%dd%HH%MM%SS%micro_seconds
- the extension can be `.json` or `.json.zip`. The latter one indicates that the file has been zipped to reduce the size and been able to include it in the repo


