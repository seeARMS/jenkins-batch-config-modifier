import urllib2
import xml.etree.ElementTree as ET
import sys
import argparse

URL = "http://your_url_here:8080"

# Edit these functions to match the modifications you'd like to make
def setXmlValue(xmlConfig, xmlPath, value):
"""Sets the element existing in the xmlConfig, specified by the xmlPath,
to the specified value."""
	try:
		xmlConfig.find(xmlPath).text = value
	except AttributeError, e:
		print("AttributeError exception occurred for XML path %s = %s") % (xmlPath, value)
 
def setCoberturaXmlValue(xmlConfig, name, lineValue, conditionalValue):
"""Sets both the LINE and CONDITIONAL coverages, existing in the xmlConfig, to the 
specified values."""
	xPath = ".//%s/targets/entry" % name
	
	path = xmlConfig.findall(xPath)
	
	if len(path) == 0:
		raise Exception("Cobertura config not found!")
	
	for entry in xmlConfig.findall(xPath):
		if entry.find('hudson.plugins.cobertura.targets.CoverageMetric').text == 'LINE':
			entry.find('int').text = lineValue
		elif entry.find('hudson.plugins.cobertura.targets.CoverageMetric').text == 'CONDITIONAL':
			entry.find('int').text = conditionalValue
		else:
			print("Cobertura coverage metric not found!")
			
			
def parseXMLTree(jobName, jobConfig):
"""Parses the XML tree, running the modifications on individual elements."""
	config = jobConfig.find('publishers')

	# set value for CheckStyle
	setXmlValue(config, 'hudson.plugins.checkstyle.CheckStylePublisher/thresholds/unstableTotalAll', "25")
	
	# set value for FindBugs
	setXmlValue(config, 'hudson.plugins.findbugs.FindBugsPublisher/thresholds/unstableTotalAll', "2")
	
	try:
		setCoberturaXmlValue(config, "healthyTarget", "7500000", "6500000")
		setCoberturaXmlValue(config, "unhealthyTarget", "6500000", "5500000")
		setCoberturaXmlValue(config, "failingTarget", "7500000", "6500000")
	except Exception, e:
		print (e.message)
	else:
		print(postConfig(jobName, jobConfig))
		
def getConfig(name):
"""Retrieves the config from the server."""
	url = "%s/job/%s/config.xml" % (URL, name)
	
	try:
		xmlConfig = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		print('HTTPError %s occured for project %s') % (str(e.code), name)
	except urllib2.URLError, e:
		print('URLError %s occured for project %s') % (str(e.reason), name)
	except Exception:
		import traceback
		print('generic exception %s occurred for project %s') % (traceback.format_exc(), name)
	else:
		return ET.parse(xmlConfig)

		
def postConfig(name, config):
"""POSTs the config back to the server"""
	url = "%s/job/%s/config.xml" % (URL, name)
	data = ET.tostring(config.getroot())
	
	try:
		response = urllib2.urlopen(url, data)
	except urllib2.HTTPError, e:
		print('HTTPError %s occured for project %s') % (str(e.code), name)
	except urllib2.URLError, e:
		print('URLError %s occured for project %s') % (str(e.reason), name)
	except Exception:
		import traceback
		print('generic exception %s occurred for project %s') % (traceback.format_exc(), name)
	else:
		return response.read()
			
def prepareJobs(projectList):
"""Verify the jobs exist on the server, and add them to a dictionary	"""

	print "Verifying that all jobs exist on the server...\n"
	
	projects = {}
	
	for jobName in projectList:
		config = getConfig(jobName)
		
		if config is None:
			print("Job %s does not exist on the server") % jobName
			var = raw_input("Skip this project and continue? (Y/n)")
			if var not in ("Y", "y"):
				sys.exit("Script exiting")
		else:	
			projects[jobName] = config
	
	return projects
			
def main(projectList):
	jobs = prepareJobs(projectList)

	# Iterate over all jobs, processing each
	for jobName, jobConfig in jobs.iteritems():
		print "Processing %s" % jobName
		
		parseXMLTree(jobName, jobConfig)
		
		print "%s complete\n" % jobName

if __name__ == '__main__':
	projectList = list()
	
	parser = argparse.ArgumentParser(description='Retrieve a Jenkins job config from the server, parse it, and POST it back.')
	parser.add_argument('-f', '--file', help="name of input file. It needs to contain one job per line", type=argparse.FileType('r'))
	parser.add_argument('jobNames', metavar='N', nargs='*', help='name of the jobs')
	
	args = parser.parse_args()

	if args.jobNames is not None:
		projectList = projectList + args.jobNames
	if args.file is not None:
		projectList = projectList + [line.strip() for line in args.file]
		
	# The user did not specify any jobs, so the project list is empty
	if not projectList:
		sys.exit("You must specify at least one job")
	
	main(projectList)