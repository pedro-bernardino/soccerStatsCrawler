import json
import serverUtils
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)




def awayStats(team):
	req = requests.post(
		'https://127.0.0.1/awaystats/',
		team, 
		verify 	= False, 
		auth 	= HTTPBasicAuth('user', 'pass'))
	
	try:
		resp = json.loads(req.content)
		serverUtils.pprint(resp)
	except Exception as e:
		print ('err: ' + req.content)

def homeStats(team):
	req = requests.post(
		'https://127.0.0.1/homestats/',
		team, 
		verify 	= False, 
		auth 	= HTTPBasicAuth('user', 'pass'))
	
	try:
		resp = json.loads(req.content)
		serverUtils.pprint(resp)
	except Exception as e:
		print ('err: ' + req.content)

def totalStats(team):
	req = requests.post(
		'https://127.0.0.1/totalstats/',
		team, 
		verify 	= False, 
		auth 	= HTTPBasicAuth('user', 'pass'))
	
	try:
		resp = json.loads(req.content)
		serverUtils.pprint(resp)
	except Exception as e:
		print ('err: ' + req.content)

def dualStats(hTeam, aTeam):
	req = requests.post(
		'https://127.0.0.1/dualstats/',
		json.dumps([hTeam, aTeam]), 
		verify 	= False, 
		auth 	= HTTPBasicAuth('user', 'pass'))
	
	try:
		resp = json.loads(req.content)
		return resp
	except Exception as e:
		resp = ('err: ' + req.content)
		return resp


if __name__ == '__main__':
	print ('\nThis is not a executable. Use restServer.py!!!\n')
	pass