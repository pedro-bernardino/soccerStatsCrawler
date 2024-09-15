# coding=utf-8
import json
import readWriteToDisk
import os


''' Return Championships id's, etc '''
def getChampionshipsDict():
	championships = {
					33561 : 'Portugal - Primeira Liga - 16/17',
					32887 : 'England - Premier League - 16/17',
					33225 : 'Germany - Bundesliga - 16/17',
					33529 : 'Spain - Primera Division - 16/17',
					32621 : 'France - Ligue 1 - 16/17',
					33771 : 'Italy - Serie A - 16/17',
					# 33061 : 'Netherlands - Eredivisie - 16/17',
					# 33217 : 'Ukraine - Premier League - 16/17',
					# 34421 : 'Argentina - Primera Division - 16/17',
					# 12825 : 'Brazil - Serie A - 2016'
					}
	return championships

def getChampionshipsIdsList():
	return getChampionshipsDict().keys()
	pass

def getChampionshipsNameFromID(id):
	return getChampionshipsDict()[id]
	pass


''' Return Path '''
def getRestWebServerPath():
	workingDir = os.path.dirname(os.path.realpath(__file__))
	folderPath = '/restWebserver.py'
	path = workingDir + folderPath
	return path

def getLocalCrawlerJsonFilePath(championshipID):
	workingDir = os.path.dirname(os.path.realpath(__file__))
	folderPath = '/dbData/crawlerJsonData/'
	path = workingDir + folderPath
	if not os.path.exists(path):
		print ("No directory crawlerJsonData found. Creating one...")
		os.makedirs(path)
	return path + str(championshipID) + '.json'

def getLocalStatsJsonFilePath(championshipID):
	workingDir = os.path.dirname(os.path.realpath(__file__))
	folderPath = '/dbData/statsJsonData/'
	path = workingDir + folderPath
	if not os.path.exists(path):
		print ("No directory statsJsonData found. Creating one...")
		os.makedirs(path)
	return path + str(championshipID) + '.json'

def getLocalSimulatorStatsJsonFilePath(championshipID):
	workingDir = os.path.dirname(os.path.realpath(__file__))
	folderPath = '/dbData/simulatorStatsJsonData/'
	path = workingDir + folderPath
	if not os.path.exists(path):
		print ("No directory statsJsonData found. Creating one...")
		os.makedirs(path)
	return path + str(championshipID) + '.json'

def getLocalTipsJsonFilePath():
	workingDir = os.path.dirname(os.path.realpath(__file__))
	folderPath = '/dbData/'
	path = workingDir + folderPath
	if not os.path.exists(path):
		print ("No directory statsJsonData found. Creating one...")
		os.makedirs(path)
	return path + 'tips.json'

def getLocalDbJsonFilePath():
	workingDir = os.path.dirname(os.path.realpath(__file__))
	folderPath = '/dbData/'
	path = workingDir + folderPath
	if not os.path.exists(path):
		print ("No directory statsJsonData found. Creating one...")
		os.makedirs(path)
	return path + 'db.json'

def getDropboxCrawlerJsonFilePath(championshipID):
	path = "/dbData/crawlerJsonData/"
	return path + str(championshipID) + '.json'

def getDropboxStatsJsonFilePath(championshipID):
	path = "/dbData/statsJsonData/"
	return path + str(championshipID) + '.json'

def getDropboxSimulatorStatsJsonFilePath(championshipID):
	path = "/dbData/simulatorStatsJsonData/"
	return path + str(championshipID) + '.json'

def getDropboxTipsJsonFilePath():
	path = "/dbData/tips.json"
	return path

def getDropboxDbJsonFilePath():
	path = "/dbData/db.json"
	return path


''' Return Files '''
def getCrawlerFilefromDisk(championshipID):
	try: # trying to find the file for the championship ID
		filefromDisk = readWriteToDisk.readJsonData(getLocalCrawlerJsonFilePath(championshipID))
		return filefromDisk
	except Exception as e:
		# print "NO FILE FOUND"
		# print e
		return []

def getStatsFilefromDisk(championshipID):
	try: # trying to find the file for the championship ID
		filefromDisk = readWriteToDisk.readJsonData(getLocalStatsJsonFilePath(championshipID))
		return filefromDisk
	except Exception as e:
		# print "NO FILE FOUND"
		# print e
		return []

def getSimulatorFilefromDisk(championshipID):
	try: # trying to find the file for the championship ID
		filefromDisk = readWriteToDisk.readJsonData(getLocalSimulatorStatsJsonFilePath(championshipID))
		return filefromDisk
	except Exception as e:
		# print "NO FILE FOUND"
		# print e
		return []

def getTipsFilefromDisk():
	try: # trying to find the file for the championship ID
		filefromDisk = readWriteToDisk.readJsonData(getLocalTipsJsonFilePath())
		return filefromDisk
	except Exception as e:
		# print "NO FILE FOUND"
		# print e
		return []

def getDbFilefromDisk():
	try: # trying to find the file for the championship ID
		filefromDisk = readWriteToDisk.readJsonData(getLocalDbJsonFilePath())
		return filefromDisk
	except Exception as e:
		# print "NO FILE FOUND"
		# print e
		return []

''' utils '''
def pprint(arg):
	try:
		result = json.dumps(arg, indent=2, sort_keys=True, separators=(',', ' : '))
		print (result)
	except Exception as e:
		result = 'pprint Err: ' + str(arg)
		print (result)

def jsonImport(arg):
	try:
		result = json.loads(arg)
		return result
	except Exception as e:
		result = 'jsonImport Err: ' + str(arg)
		return result

def jsonExport(arg):
    try:
        result = json.dumps(arg, sort_keys=True, indent=2, separators=(',', ': '))
        print (result)
        return result
    except Exception as e:
        result = 'jsonExport Err: ' + str(arg)
        return result

def stopProgram():
	print ("stopping the program...")
	raise SystemExit(0)
	pass

def pause():
	raw_input("Press any key to continue...")
	pass






if __name__ == '__main__':
    print ('\nThis is not a executable. Use the import to get the functions!!!\n')
    # import serverUtils
    # import inspect
    # functs = inspect.getmembers(serverUtils, inspect.isfunction)
    # methods = [x[0] for x in functs]
    # public = [i for i in methods if not i.startswith('_')]
    # serverUtils.pprint(public)
    pass