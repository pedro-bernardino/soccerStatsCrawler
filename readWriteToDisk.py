# coding=utf-8
import json, os

def readJsonData(fileNamePath):
	with open(fileNamePath) as data_file:    
		return json.load(data_file)
	return None

def writeJsonData(jsonData, toFileNamePath):
	with open(toFileNamePath, 'w') as outfile:
		json.dump(jsonData, outfile, indent=4, separators=(',', ' : '))

if __name__ == '__main__':
    print ('\nThis is not a executable. Use the import to get the functions!!!\n')
    print ('Public functions:')
    print ('readJsonData(fileNamePath):')
    print ('writeJsonData(jsonData, toFileNamePath):')