import subprocess
import sys, json
import serverUtils

def status():
	print ('Server Status:')
	process = subprocess.Popen([
		'ps',
		'-f',
		'-C',
		'python'
		],
		shell=False,
		stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	communicationData = process.communicate()
	comunicationArray = communicationData[0].split('\n')

	processCount = 0
	for x in xrange(1,len(comunicationArray)-1):
		item = comunicationArray[x]
		itemArr = item.split(' ')
		for subItemNr in xrange(0,len(itemArr)):
			if itemArr[subItemNr] == 'python' and itemArr[subItemNr+1] == serverUtils.getRestWebServerPath():
				processCount = 1
				break
				
	if processCount == 1:
		print ('REST server is running')
	else:
		print ('REST Server is Stopped')


def start():
	stop_action()
	print ('Starting REST server')
	start_action()
	print ('REST server is running')

def stop():
	print ('Stoping REST server...')
	stop_action()
	print ('REST Server Stopped')

def restart():
	print ('Stoping REST server...')
	stop_action()
	print ('REST Server Stopped')
	print ('Starting REST server')
	start_action()
	print ('REST server is running')

def start_action():
	process = subprocess.Popen([
		'python',
		serverUtils.getRestWebServerPath()
		])
def stop_action():
	process = subprocess.Popen([
		'pkill', 
		'-9', 
		'-f',
		'python ' + serverUtils.getRestWebServerPath()
		],
		shell=False,
		stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	communicationData = process.communicate()
	

def invalidArgs():
	print ('Invalid Argument')
	print ('Use: start, stop, restart or status')

if __name__ == '__main__':
	# print 'Number of arguments:', len(sys.argv), 'arguments.'
	# print 'Argument List:', str(sys.argv)

	if len(sys.argv) == 2:
		arg = sys.argv[1]
		if arg == 'start':
			start()
		elif arg == 'stop':
			stop()
		elif arg == 'restart':
			restart()
		elif arg == 'status':
			status()
		else:
			invalidArgs()
	else:
		invalidArgs()