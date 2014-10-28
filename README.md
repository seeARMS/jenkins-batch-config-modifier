jenkins-batch-config-modifier
=============================

A python script used to batch-modify configuration files for jobs hosted on a Je
nkins server.

Description
----------
This is a simple script I created during my time at Blackberry when I needed to
modify a large number of Jenkins jobs.
Specifically, I needed to change the threshold values for numerous options, incl
uding cobertura code coverage, however this script can easily be modified to acc
ommodate for any modifications that need to be made.

This script retrieves the config.xml for the required jobs from your Jenkins ser
ver, traverses the XML and makes any changes you'd like, then finally POSTs it b
ack to the server.

Installation
------------
Clone this repo, and make the following changes to update-config.py:
  - Change the URL var to point to the URL of your Jenkins server
  - Edit the setXMLValue, setCoberturaXMLValue, and parseXML methods to run whichever modifications you'd like 
  - If you need to run the script on many different jobs, consider creating a file (listing one job per line). See below.

Usage
-----
You may pass in the job names as command-line arguments, and/or you may pass in
a file with one job name per line (using the -f flag).

Run the program with no arguments and the -h flag to display the help.


```py
python update-config.py [-f FILE] [N [N ...]]

N:                          name of the jobs

-f FILE, --file FILE:       name of the input file. This file needs to contain one job name per line

```
If both N and -f are included, the script processes the jobs included in both.

