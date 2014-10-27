import urllib2
import xml.etree.ElementTree as ET
import sys
import argparse

# returns the ElementTree object from the server
def getConfig(name):
	url = "http://10.236.34.84:8080/job/%s/config.xml" % name
	
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
	
def main(projects):
	#First check to verify all projects exist
	print "Verifying that all projects exist on the server...\n"
	
	projectList = list()
	for p in projects:
		if getConfig(p) is None:
			print("Project %s does not exist on the server") % p
			var = raw_input("Skip this project and continue? (Y/n)")
			if var not in ("Y", "y"):
				sys.exit("Script exiting")
			
		projectList.append(p)

	for p in projectList:

		print "Processing %s" % p

		globalConfig = getConfig(p)
	
		# if an error occurred, skip this project
		if (globalConfig is None):
			continue
			
		config = globalConfig.find('publishers')
		
		# set value for CheckStyle
		setXmlValue(config, 'hudson.plugins.checkstyle.CheckStylePublisher/thresholds/unstableTotalAll', "25")
		
		# set value for FindBugs
		setXmlValue(config, 'hudson.plugins.findbugs.FindBugsPublisher/thresholds/unstableTotalAll', "2")
		
		setCoberturaXmlValue(config, "healthyTarget", 7500000, 6500000)
		setCoberturaXmlValue(config, "unhealhtyTarget", 6500000 , 5500000)
		setCoberturaXmlValue(config, "healthyTarget", 7500000, 6500000)

		globalConfig.write(p + ".xml")
		print "%s complete\n" % p

		#ET.tostring(config)


if __name__ == '__main__':
	projectList = list()
	
	parser = argparse.ArgumentParser(description='Retrieve a Jenkins job config from the server, parse it, and POST it back.')
	parser.add_argument('-f', '--file', help="Name of file containing one job per line", type=argparse.FileType('r'))
	parser.add_argument('jobNames', metavar='N', nargs='*', help='job names')
	
	args = parser.parse_args()
			
	if (args.jobNames is not None):
		projectList = projectList + args.jobNames
	if (args.file is not None):
		projectList = projectList + [line.strip() for line in args.file]
	
	main(projectList)