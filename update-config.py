import urllib2
import xml.etree.ElementTree as ET
import sys
import argparse

########## Change these methods to match the modifications you'd like to make ##########
def setXmlValue(xmlConfig, xmlPath, value):
	try:
		xmlConfig.find(xmlPath).text = value
	except AttributeError, e:
		print("AttributeError exception occurred for XML path %s = %s") % (xmlPath, value)
 
def setCoberturaXmlValue(xmlConfig, name, lineValue, conditionalValue):
	xPath = ".//*[@name='%s']/targets/entry" % name

	for entry in xmlConfig.findall(xPath):
		if entry.find('hudson.plugins.cobertura.targets.CoverageMetric') == 'LINE':
			entry.find('int').text = lineValue
		elif entry.find('hudson.plugins.cobertura.targets.CoverageMetric') == 'CONDITIONAL':
			entry.find('int').text = conditionalValue
		else:
			print "Cobertura entry not found!"
			
def runModifications(jobName, jobConfig):
	config = jobConfig.find('publishers')
	
	# set value for CheckStyle
	setXmlValue(config, 'hudson.plugins.checkstyle.CheckStylePublisher/thresholds/unstableTotalAll', "25")
	
	# set value for FindBugs
	setXmlValue(config, 'hudson.plugins.findbugs.FindBugsPublisher/thresholds/unstableTotalAll', "2")
	
	setCoberturaXmlValue(config, "healthyTarget", 7500000, 6500000)
	setCoberturaXmlValue(config, "unhealhtyTarget", 6500000 , 5500000)
	setCoberturaXmlValue(config, "healthyTarget", 7500000, 6500000)
		
def getConfig(name):
	url = "http://your_url:8080/job/%s/config.xml" % name
	
	try:
		xmlConfig = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		print('HTTPError %s occured for project %s') % (str(e.code), name)
	except urllib2.URLError, e:
		print('URLError %s occured for project %s') % (str(e.reason), name)
	except httplib.HTTPException, e:
		print('HTTPException occured for project %s') % (name)
	except Exception:
		import traceback
		print('generic exception %s occurred for project %s') % (traceback.format_exc(), name)
	else:
		return ET.parse(xmlConfig)

# Verify the jobs exist on the server, and add them to a dictionary		
def prepareJobs(projectList):
	print "Verifying that all jobs exist on the server...\n"
	
	#projects = list()
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
			#projects.append(p)
	
	return projects
			
def main(projectList):
	jobs = prepareJobs(projectList)

	for jobName, jobConfig in jobs.iteritems():
		print "Processing %s" % jobName
		
		runModifications(jobName, jobConfig)
		
		jobConfig.write(jobName + ".xml")
		print "%s complete\n" % jobName

if __name__ == '__main__':
	projectList = list()
	
	parser = argparse.ArgumentParser(description='Retrieve a Jenkins job config from the server, parse it, and POST it back.')
	parser.add_argument('-f', '--file', help="name of input file. It needs to contain one job per line", type=argparse.FileType('r'))
	parser.add_argument('jobNames', metavar='N', nargs='*', help='name of the jobs')
	
	args = parser.parse_args()

	if (args.jobNames is not None):
		projectList = projectList + args.jobNames
	if (args.file is not None):
		projectList = projectList + [line.strip() for line in args.file]
	
	main(projectList)