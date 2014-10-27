jenkins-batch-config-modifier
=============================

A python script used to batch-modify configuration files for jobs hosted on a Jenkins server.

Description
----------
This is a simple script I created during my time at Blackberry when I needed to modify a large number of Jenkins jobs. I needed to change the threshold values for numerous options, including cobertura code coverage.

This script retrieves the config.xml from any jobs you'd like to change from your Jenkins server, traverses the XML and makes any changes you'd like, then finally POSTs it back to the server.

Usage
-----
You may pass in the job names as command-line arguments, or you may pass in a file with one job name per line (using the -f flag).

python update-config.py [-f filename] [jobname1 jobname2 ...] 

