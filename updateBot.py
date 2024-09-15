import subprocess
import serverUtils
import updateDB
import os
import signal

def __isXvfbRunning__():
	# ps -f -C Xvfb
	# ps -f -C xvfb-run
	process = subprocess.Popen([
		'ps',
		'-f',
		'-C',
		'Xvfb'
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
			if itemArr[subItemNr] == 'Xvfb' or itemArr[subItemNr] == 'xvfb-run': # and itemArr[subItemNr+1] == serverUtils.getRestWebServerPath():
				processCount = 1
				break
				
	if processCount > 0:
		return True
	else:
		return False

def __stop_xvfb__():
	# pkill -9 -f Xvfb
	#
	process = subprocess.Popen([
		'pkill', 
		'-9', 
		'-f',
		'Xvfb'
		],
		shell=False,
		stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	communicationData = process.communicate()
	print (communicationData)


def __start_bot__():
	print (serverUtils.getUpdateDBPath())
	process = subprocess.Popen([
		'xvfb', 
		'python', 
		serverUtils.getUpdateDBPath()
		],
		shell=False,
		stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	communicationData = process.communicate()
	print (communicationData)



if __name__ == '__main__':
	pid = int(open('/tmp/.X%s-lock' % 99).read().strip())
	print (os.kill(pid, signal.SIGINT))
	
	# if __isXvfbRunning__():
	# 	print 'Xvfb is running'
	# 	__stop_xvfb__()
	# else:
	# 	print 'Xvfb is NOT running'
	# 	__start_bot__()


