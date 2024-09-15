# coding=utf-8
import time
import datetime
import serverConstants as CONST
import serverUtils
import bfCrawler
import readWriteToDisk
import dropboxAPI
import sendServerEmail
import tips
import requests
from copy import deepcopy
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
#######################################################################################
									Crawler
#######################################################################################
'''
def __startCrawler__():
	log = []
	for id in serverUtils.getChampionshipsIdsList():
		champIDString = str(id)

		filefromDisk = serverUtils.getCrawlerFilefromDisk(id)
		if len(filefromDisk) == 0:
			tempLog = "Championship {} not found. Creating one...".format(serverUtils.getChampionshipsNameFromID(id))
			log.append(tempLog)
			print (tempLog)

			championshipFixtures = []
			try:
				championshipFixtures = bfCrawler.getChampionshipFixtures(id)
				readWriteToDisk.writeJsonData(championshipFixtures, serverUtils.getLocalCrawlerJsonFilePath(id))
				pass
			except Exception as e:
				tempLog = "bfCrawler.getChampionshipFixtures(id) FAILED: id = {}".format(id) + ' - ' + str(e)
				log.append(tempLog)
				print (tempLog)
		else:
			tempLog = "{} file found. Updating...".format(serverUtils.getChampionshipsNameFromID(id))
			log.append(tempLog)
			print (tempLog)

			localFileGameList	= sorted(filefromDisk, key=lambda k: k[CONST.GAME_DATE_TO_SORT])
			webUpdatedGameList 	= sorted(bfCrawler.gameListFromChampionshipID(id), key=lambda k: k[CONST.GAME_DATE_TO_SORT])

			# Get games to update:
			updateCount = 0

			localGamesWithFTResult 	= [game for game in localFileGameList 	if game[CONST.GAME_FT_SCORE] != '']
			webgamesWithFTResult 	= [game for game in webUpdatedGameList 	if game[CONST.GAME_FT_SCORE] != '']
			
			finalgamesDictToSaveLocally = []


			if len(localFileGameList) == len(localGamesWithFTResult) and len(localGamesWithFTResult) == len(webgamesWithFTResult):
				log.append('League finish! Skiping...')
				print ('League finish! Skiping...')
				continue # skip

			

			for webGame in webUpdatedGameList:
				webGameID = webGame[CONST.GAME_ID]

				localGameTest = next((game for game in localGamesWithFTResult if game[CONST.GAME_ID] == webGameID), None)

				if localGameTest != None and localGameTest[CONST.GAME_FT_SCORE] != '' and localGameTest[CONST.GAME_HF_SCORE] != '':
					finalgamesDictToSaveLocally.append(localGameTest)
				else:
					if webGame[CONST.GAME_FT_SCORE] != '' and webGame[CONST.GAME_HF_SCORE] != '':
						# go online to get the new data (need to merge gameDict with the result)
						updatedWebGame = bfCrawler.gameInfoFromMatchID(webGameID)
						gameUpdated = dict(deepcopy(webGame), **updatedWebGame)
						finalgamesDictToSaveLocally.append(gameUpdated)
						updateCount += 1
						pass
					else:
						finalgamesDictToSaveLocally.append(webGame)	
				# break


			if updateCount > 0:
				championshipsIdsToUploadDropbox.append(id)
				tempLog = '{} game{} updated'.format(updateCount, 's' if updateCount > 1 else '')
				log.append(tempLog)
				print (tempLog)
				# update local file
				readWriteToDisk.writeJsonData(finalgamesDictToSaveLocally, serverUtils.getLocalCrawlerJsonFilePath(id))
				pass
			else:
				# dont update Local file! nothing changed!
				tempLog = 'Nothing changed. Local file is updated!'
				log.append(tempLog)
				print (tempLog)
				pass

		# break
	return log


'''
#######################################################################################
							RoundsStats_Calculations
#######################################################################################
'''
def __start_RoundsStats_Calculations__():
	if len(championshipsIdsToUploadDropbox) == 0:
		log = []
		tempLog = 'Noting Changed! All Files are updated.'
		log.append(tempLog)
		print (tempLog)
		return log

	# funcao para calculo dos rankings
	def __get_rankings__(teamsStatsDictionary):
		teams 				= teamsStatsDictionary.keys()
		classificationDic 	= {}
		defenceDic			= {}
		attackDic			= {}
	
		#get totals GF/GA
		totalGF = 0
		totalGA = 0
		for team in teams:
			totalGF += teamsStatsDictionary[team][CONST.TEAM_GOALS_FOR]
			totalGA += teamsStatsDictionary[team][CONST.TEAM_GOALS_AGAINST]
	
		# TEAM_CLASSIFICATION
		tempClassificationDic = {}
		for team in teams:
			points 		= teamsStatsDictionary[team][CONST.TEAM_POINTS]
			goalsDif 	= teamsStatsDictionary[team][CONST.TEAM_GOALS_DIF]
			goalsFor 	= teamsStatsDictionary[team][CONST.TEAM_GOALS_FOR]
			wins 		= teamsStatsDictionary[team][CONST.TEAM_WINS]
			classificationRank = points + goalsDif/10.000 + goalsFor/100.000 + wins/1000.000
			tempClassificationDic[team] = classificationRank
	
		classificationList = sorted(tempClassificationDic.keys(), key=lambda k: tempClassificationDic[k])[::-1]
		for team in classificationList:
			classificationDic[team] = classificationList.index(team) + 1
	
		# TEAM_DEFENSE_RANKING
		tempDefenceDic = {}
		averageGA = totalGF/float(len(teams))
		for team in teams:
			conseadFist 	= teamsStatsDictionary[team][CONST.TEAM_CONSEAD_FIRST]
			loses 			= teamsStatsDictionary[team][CONST.TEAM_LOSES]
			points 			= teamsStatsDictionary[team][CONST.TEAM_POINTS]
			goalsAgainst 	= teamsStatsDictionary[team][CONST.TEAM_GOALS_AGAINST]
			goalsAgainstRQ	= goalsAgainst/float(averageGA) if averageGA > 0 else 0
			defenceRanking 	= goalsAgainstRQ + conseadFist/100.000 + loses/500.000 - points/1000.000
			tempDefenceDic[team] = defenceRanking
	
		defenceList = sorted(tempDefenceDic.keys(), key=lambda k: tempDefenceDic[k])[::1]
		for team in defenceList:
			defenceDic[team] = defenceList.index(team) + 1
	
		# TEAM_ATACK_RANKING
		tempAttackDic = {}
		averageGF = totalGA/float(len(teams))
		for team in teams:
			scoreFist 		= teamsStatsDictionary[team][CONST.TEAM_SCORE_FIRST]
			wins 			= teamsStatsDictionary[team][CONST.TEAM_WINS]
			points 			= teamsStatsDictionary[team][CONST.TEAM_POINTS]
			goalsfor 		= teamsStatsDictionary[team][CONST.TEAM_GOALS_FOR]
			goalsforRQ		= goalsfor/float(averageGF) if averageGF > 0 else 0
			attackRanking 	= goalsforRQ + scoreFist/100.000 + wins/500.000 + points/1000.000
			tempAttackDic[team] = attackRanking
	
		attackList = sorted(tempAttackDic.keys(), key=lambda k: tempAttackDic[k])[::-1]
		for team in attackList:
			attackDic[team] = attackList.index(team) + 1
	
		# All done, Returning...
		returnDic = {}
		returnDic[CONST.TEAM_CLASSIFICATION]	= classificationDic
		returnDic[CONST.TEAM_DEFENSE_RANKING]	= defenceDic
		returnDic[CONST.TEAM_ATACK_RANKING] 	= attackDic
	
		return returnDic

	calcLog = []
	# loop in crawler files run 1 (Home/Away stats)
	for champID in championshipsIdsToUploadDropbox: #serverUtils.getChampionshipsIdsList():
		champIDString = str(champID)
		
		tempLog = 'Calculatting: ' + serverUtils.getChampionshipsNameFromID(champID) + ' - ID: ' + champIDString
		calcLog.append(tempLog)
		print (tempLog)

		gameNumber = 0
		homeStatsDicTemp 			= {}
		awayStatsDicTemp 			= {}
		totalStatsDicTemp 			= {}
		fixturesStatsDic			= {}

		fullFixturesSimulatorStatsArr = []

		filefromDisk = serverUtils.getCrawlerFilefromDisk(champID)
		
		gamesPlayedFromDiskFile = [game for game in filefromDisk if game[CONST.GAME_FT_SCORE] != '']
		gamesPlayedSorted	= sorted(gamesPlayedFromDiskFile, key=lambda k: k[CONST.GAME_DATE_TO_SORT])

		for game in gamesPlayedSorted: #get games sorted!
			gameNumber += 1
			# print '[' + str('{0:03}'.format(gameNumber)) + '] ' + game[CONST.GAME_ID] + ' - ' + game[CONST.GAME_DATE] + ' => ' + game[CONST.GAME_HOME_TEAM] + ' vs ' + game[CONST.GAME_AWAY_TEAM] + ' (' + game[CONST.GAME_FT_SCORE] + ')'
			# pprint(game)
			
			# home vars
			gameHomeTeamID 	= game[CONST.GAME_HOME_TEAM] + ' ' + champIDString
			gameHomeHTGoals	= int(game[CONST.GAME_HF_SCORE].split('-')[0]) if game[CONST.GAME_HF_SCORE] != '' else 0
			gameHomeFTGoals	= int(game[CONST.GAME_FT_SCORE].split('-')[0])
			gameHomeTeam 	= game[CONST.GAME_HOME_TEAM]
			gameHomeTeamKEY	= gameHomeTeam#.replace('.','%')
			gameHomeManager = game[CONST.GAME_DETAILS][CONST.DETAILS_HOME_MANAGER] 	if CONST.DETAILS_HOME_MANAGER 	in game[CONST.GAME_DETAILS] else ''
			gameHomeShirt	= game[CONST.GAME_DETAILS][CONST.DETAILS_HOME_SHIRT] 	if CONST.DETAILS_HOME_SHIRT		in game[CONST.GAME_DETAILS] else ''
			gameHomeLogo	= game[CONST.GAME_HOME_LOGO]							if CONST.GAME_HOME_LOGO 		in game 					else ''
			gameHomeStadium	= game[CONST.GAME_DETAILS][CONST.DETAILS_STADIUM] 		if CONST.DETAILS_STADIUM		in game[CONST.GAME_DETAILS] else ''
			# away vars
			gameAwayTeamID 	= game[CONST.GAME_AWAY_TEAM] + ' ' + champIDString 
			gameAwayHTGoals	= int(game[CONST.GAME_HF_SCORE].split('-')[1]) if game[CONST.GAME_HF_SCORE] != '' else 0
			gameAwayFTGoals	= int(game[CONST.GAME_FT_SCORE].split('-')[1])
			gameAwayTeam 	= game[CONST.GAME_AWAY_TEAM]
			gameAwayTeamKEY	= gameAwayTeam#.replace('.','%')
			gameAwayManager = game[CONST.GAME_DETAILS][CONST.DETAILS_AWAY_MANAGER] 	if CONST.GAME_DETAILS 	in game else ''
			gameAwayShirt	= game[CONST.GAME_DETAILS][CONST.DETAILS_AWAY_SHIRT] 	if CONST.GAME_DETAILS 	in game else ''
			gameAwayLogo	= game[CONST.GAME_AWAY_LOGO] 							if CONST.GAME_AWAY_LOGO in game else ''
			# Home calculations
			gameHomeWin		= 1 if gameHomeFTGoals  > gameAwayFTGoals else 0
			gameHomeDraw	= 1 if gameHomeFTGoals == gameAwayFTGoals else 0
			gameHomeLose	= 1 if gameHomeFTGoals  < gameAwayFTGoals else 0
			gameHomePoints	= gameHomeWin * 3 + gameHomeDraw
			gameHomeScoreF	= 0;
			# Away calculations
			gameAwayWin		= gameHomeLose
			gameAwayDraw	= gameHomeDraw
			gameAwayLose	= gameHomeWin
			gameAwayPoints	= gameAwayWin * 3 + gameAwayDraw
			gameAwayScoreF	= 0;
			# Misc calculations
			gameTotalGoals 	= gameHomeFTGoals + gameAwayFTGoals
			gameNoGoals 	= 1 if gameHomeFTGoals + gameAwayFTGoals == 0 else 0
			gameUnder15		= 1 if gameHomeFTGoals + gameAwayFTGoals  < 2 else 0
			gameUnder25		= 1 if gameHomeFTGoals + gameAwayFTGoals  < 3 else 0
			gameUnder35		= 1 if gameHomeFTGoals + gameAwayFTGoals  < 4 else 0
			gameOver15		= 1 - gameUnder15
			gameOver25		= 1 - gameUnder25
			gameOver35		= 1 - gameUnder35
			# First to score
			if gameTotalGoals > 0:
				scoreString = ''
				if CONST.GAME_EVENTS in game:
					if len(game[CONST.GAME_EVENTS][CONST.EVENTS_GOALS_ORDER]) > 0:
						scoreString = game[CONST.GAME_EVENTS][CONST.EVENTS_GOALS_ORDER][0]
				if scoreString == CONST.EVENTS_HOME_TEAM:
					gameHomeScoreF = 1
				elif scoreString == CONST.EVENTS_AWAY_TEAM:
					gameAwayScoreF = 1
				else:
					if gameHomeFTGoals > gameAwayFTGoals:
						gameHomeScoreF = 1
					elif gameHomeFTGoals < gameAwayFTGoals:
						gameAwayScoreF = 1

			

			# Stats Dictionarys
			myHomeTempDic = {} if gameHomeTeamKEY not in homeStatsDicTemp else homeStatsDicTemp[gameHomeTeamKEY]
			myHomeTempDic[CONST.TEAM_LEAGUE]				= champID
			myHomeTempDic[CONST.TEAM_ID]					= gameHomeTeamID
			myHomeTempDic[CONST.TEAM_NAME] 				 	= gameHomeTeam
			myHomeTempDic[CONST.TEAM_LOGO] 				 	= gameHomeLogo
			myHomeTempDic[CONST.TEAM_MANAGER] 			 	= gameHomeManager
			myHomeTempDic[CONST.TEAM_STADIUM] 			 	= gameHomeStadium
			myHomeTempDic[CONST.TEAM_SHIRT_HOME]			= gameHomeShirt

			myHomeTempDic[CONST.TEAM_WINS] 				 	= gameHomeWin		if CONST.TEAM_WINS 			not in myHomeTempDic else myHomeTempDic[CONST.TEAM_WINS] 			+ gameHomeWin
			myHomeTempDic[CONST.TEAM_DRAWS]					= gameHomeDraw		if CONST.TEAM_DRAWS 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_DRAWS]			+ gameHomeDraw
			myHomeTempDic[CONST.TEAM_LOSES]					= gameHomeLose		if CONST.TEAM_LOSES 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_LOSES]			+ gameHomeLose
			myHomeTempDic[CONST.TEAM_POINTS]				= gameHomePoints	if CONST.TEAM_POINTS 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_POINTS]			+ gameHomePoints
			myHomeTempDic[CONST.TEAM_GOALS_FOR]				= gameHomeFTGoals	if CONST.TEAM_GOALS_FOR 	not in myHomeTempDic else myHomeTempDic[CONST.TEAM_GOALS_FOR]		+ gameHomeFTGoals
			myHomeTempDic[CONST.TEAM_GOALS_AGAINST]			= gameAwayFTGoals	if CONST.TEAM_GOALS_AGAINST not in myHomeTempDic else myHomeTempDic[CONST.TEAM_GOALS_AGAINST]	+ gameAwayFTGoals
			myHomeTempDic[CONST.TEAM_GAMES]					= 1 				if CONST.TEAM_GAMES 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_GAMES]			+ 1
			myHomeTempDic[CONST.TEAM_SCORE_FIRST] 		 	= gameHomeScoreF	if CONST.TEAM_SCORE_FIRST 	not in myHomeTempDic else myHomeTempDic[CONST.TEAM_SCORE_FIRST] 	+ gameHomeScoreF
			myHomeTempDic[CONST.TEAM_CONSEAD_FIRST]			= gameAwayScoreF	if CONST.TEAM_CONSEAD_FIRST not in myHomeTempDic else myHomeTempDic[CONST.TEAM_CONSEAD_FIRST]	+ gameAwayScoreF
			myHomeTempDic[CONST.TEAM_NO_GOALS] 			 	= gameNoGoals		if CONST.TEAM_NO_GOALS 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_NO_GOALS] 		+ gameNoGoals
			myHomeTempDic[CONST.TEAM_UNDER_15] 			 	= gameUnder15		if CONST.TEAM_UNDER_15 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_UNDER_15] 		+ gameUnder15
			myHomeTempDic[CONST.TEAM_OVER_15] 			 	= gameOver15		if CONST.TEAM_OVER_15 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_OVER_15] 		+ gameOver15
			myHomeTempDic[CONST.TEAM_UNDER_25] 			 	= gameUnder25		if CONST.TEAM_UNDER_25 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_UNDER_25] 		+ gameUnder25
			myHomeTempDic[CONST.TEAM_OVER_25] 			 	= gameOver25		if CONST.TEAM_OVER_25 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_OVER_25] 		+ gameOver25
			myHomeTempDic[CONST.TEAM_UNDER_35] 			 	= gameUnder35		if CONST.TEAM_UNDER_35 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_UNDER_35] 		+ gameUnder35
			myHomeTempDic[CONST.TEAM_OVER_35] 			 	= gameOver35		if CONST.TEAM_OVER_35 		not in myHomeTempDic else myHomeTempDic[CONST.TEAM_OVER_35] 		+ gameOver35

			myHomeTempDic[CONST.TEAM_GOALS_DIF]				= myHomeTempDic[CONST.TEAM_GOALS_FOR] 			- myHomeTempDic[CONST.TEAM_GOALS_AGAINST]
			myHomeTempDic[CONST.TEAM_FORM] 		 		 	= myHomeTempDic[CONST.TEAM_POINTS] 				/ float(myHomeTempDic[CONST.TEAM_GAMES] * 3)
			myHomeTempDic[CONST.TEAM_SCORE_FIRST_BY_GAME]  	= myHomeTempDic[CONST.TEAM_SCORE_FIRST]			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_CONSEAD_FIRST_BY_GAME]	= myHomeTempDic[CONST.TEAM_CONSEAD_FIRST]		/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_NO_GOALS_BY_GAME]     	= myHomeTempDic[CONST.TEAM_NO_GOALS]			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_UNDER_15_BY_GAME]     	= myHomeTempDic[CONST.TEAM_UNDER_15]			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_OVER_15_BY_GAME]      	= myHomeTempDic[CONST.TEAM_OVER_15] 			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_UNDER_25_BY_GAME]     	= myHomeTempDic[CONST.TEAM_UNDER_25]			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_OVER_25_BY_GAME]      	= myHomeTempDic[CONST.TEAM_OVER_25] 			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_UNDER_35_BY_GAME]     	= myHomeTempDic[CONST.TEAM_UNDER_35]			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_OVER_35_BY_GAME]      	= myHomeTempDic[CONST.TEAM_OVER_35] 			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_OVER_35_BY_GAME]		= myHomeTempDic[CONST.TEAM_OVER_35] 			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_GOALS_FOR_BY_GAME]    	= myHomeTempDic[CONST.TEAM_GOALS_FOR]			/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_GOALS_AGAINST_BY_GAME]	= myHomeTempDic[CONST.TEAM_GOALS_AGAINST]		/ float(myHomeTempDic[CONST.TEAM_GAMES])
			myHomeTempDic[CONST.TEAM_GOALS_BY_GAME]        	= myHomeTempDic[CONST.TEAM_GOALS_FOR_BY_GAME] 	+ myHomeTempDic[CONST.TEAM_GOALS_AGAINST_BY_GAME]
			myHomeTempDic[CONST.TEAM_CLASSIFICATION]		= 'n/a'
			myHomeTempDic[CONST.TEAM_DEFENSE_RANKING]		= 'n/a'
			myHomeTempDic[CONST.TEAM_ATACK_RANKING]			= 'n/a'
			homeStatsDicTemp[gameHomeTeamKEY]	= deepcopy(myHomeTempDic)



			myAwayTempDic = {} if gameAwayTeamKEY not in awayStatsDicTemp else awayStatsDicTemp[gameAwayTeamKEY]
			myAwayTempDic[CONST.TEAM_LEAGUE]				= champID
			myAwayTempDic[CONST.TEAM_ID]					= gameAwayTeamID
			myAwayTempDic[CONST.TEAM_NAME] 					= gameAwayTeam
			myAwayTempDic[CONST.TEAM_LOGO] 					= gameAwayLogo
			myAwayTempDic[CONST.TEAM_MANAGER] 				= gameAwayManager
			myAwayTempDic[CONST.TEAM_SHIRT_AWAY]			= gameAwayShirt

			myAwayTempDic[CONST.TEAM_WINS] 					= gameAwayWin		if CONST.TEAM_WINS 			not in myAwayTempDic else myAwayTempDic[CONST.TEAM_WINS] 			+ gameAwayWin
			myAwayTempDic[CONST.TEAM_DRAWS]					= gameAwayDraw		if CONST.TEAM_DRAWS 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_DRAWS]			+ gameAwayDraw
			myAwayTempDic[CONST.TEAM_LOSES]					= gameAwayLose		if CONST.TEAM_LOSES 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_LOSES]			+ gameAwayLose
			myAwayTempDic[CONST.TEAM_POINTS]				= gameAwayPoints	if CONST.TEAM_POINTS 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_POINTS]			+ gameAwayPoints
			myAwayTempDic[CONST.TEAM_GOALS_FOR]				= gameAwayFTGoals	if CONST.TEAM_GOALS_FOR 	not in myAwayTempDic else myAwayTempDic[CONST.TEAM_GOALS_FOR]		+ gameAwayFTGoals
			myAwayTempDic[CONST.TEAM_GOALS_AGAINST]			= gameHomeFTGoals	if CONST.TEAM_GOALS_AGAINST not in myAwayTempDic else myAwayTempDic[CONST.TEAM_GOALS_AGAINST]	+ gameHomeFTGoals
			myAwayTempDic[CONST.TEAM_GAMES]					= 1 				if CONST.TEAM_GAMES 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_GAMES]			+ 1
			myAwayTempDic[CONST.TEAM_SCORE_FIRST] 			= gameAwayScoreF	if CONST.TEAM_SCORE_FIRST 	not in myAwayTempDic else myAwayTempDic[CONST.TEAM_SCORE_FIRST] 	+ gameAwayScoreF
			myAwayTempDic[CONST.TEAM_CONSEAD_FIRST]			= gameHomeScoreF	if CONST.TEAM_CONSEAD_FIRST not in myAwayTempDic else myAwayTempDic[CONST.TEAM_CONSEAD_FIRST]	+ gameHomeScoreF
			myAwayTempDic[CONST.TEAM_NO_GOALS] 				= gameNoGoals		if CONST.TEAM_NO_GOALS 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_NO_GOALS] 		+ gameNoGoals
			myAwayTempDic[CONST.TEAM_UNDER_15] 				= gameUnder15		if CONST.TEAM_UNDER_15 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_UNDER_15] 		+ gameUnder15
			myAwayTempDic[CONST.TEAM_OVER_15] 				= gameOver15		if CONST.TEAM_OVER_15 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_OVER_15] 		+ gameOver15
			myAwayTempDic[CONST.TEAM_UNDER_25] 				= gameUnder25		if CONST.TEAM_UNDER_25 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_UNDER_25] 		+ gameUnder25
			myAwayTempDic[CONST.TEAM_OVER_25] 				= gameOver25		if CONST.TEAM_OVER_25 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_OVER_25] 		+ gameOver25
			myAwayTempDic[CONST.TEAM_UNDER_35] 				= gameUnder35		if CONST.TEAM_UNDER_35 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_UNDER_35] 		+ gameUnder35
			myAwayTempDic[CONST.TEAM_OVER_35] 				= gameOver35		if CONST.TEAM_OVER_35 		not in myAwayTempDic else myAwayTempDic[CONST.TEAM_OVER_35] 		+ gameOver35
			
			myAwayTempDic[CONST.TEAM_GOALS_DIF]				= myAwayTempDic[CONST.TEAM_GOALS_FOR] 			- myAwayTempDic[CONST.TEAM_GOALS_AGAINST]
			myAwayTempDic[CONST.TEAM_FORM] 		 		 	= myAwayTempDic[CONST.TEAM_POINTS] 				/ float(myAwayTempDic[CONST.TEAM_GAMES] * 3)
			myAwayTempDic[CONST.TEAM_SCORE_FIRST_BY_GAME]  	= myAwayTempDic[CONST.TEAM_SCORE_FIRST]			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_CONSEAD_FIRST_BY_GAME]	= myAwayTempDic[CONST.TEAM_CONSEAD_FIRST]		/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_NO_GOALS_BY_GAME]     	= myAwayTempDic[CONST.TEAM_NO_GOALS]			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_UNDER_15_BY_GAME]     	= myAwayTempDic[CONST.TEAM_UNDER_15]			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_OVER_15_BY_GAME]      	= myAwayTempDic[CONST.TEAM_OVER_15] 			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_UNDER_25_BY_GAME]     	= myAwayTempDic[CONST.TEAM_UNDER_25]			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_OVER_25_BY_GAME]      	= myAwayTempDic[CONST.TEAM_OVER_25] 			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_UNDER_35_BY_GAME]     	= myAwayTempDic[CONST.TEAM_UNDER_35]			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_OVER_35_BY_GAME]      	= myAwayTempDic[CONST.TEAM_OVER_35] 			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_OVER_35_BY_GAME]		= myAwayTempDic[CONST.TEAM_OVER_35] 			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_GOALS_FOR_BY_GAME]    	= myAwayTempDic[CONST.TEAM_GOALS_FOR]			/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_GOALS_AGAINST_BY_GAME]	= myAwayTempDic[CONST.TEAM_GOALS_AGAINST]		/ float(myAwayTempDic[CONST.TEAM_GAMES])
			myAwayTempDic[CONST.TEAM_GOALS_BY_GAME]        	= myAwayTempDic[CONST.TEAM_GOALS_FOR_BY_GAME] 	+ myAwayTempDic[CONST.TEAM_GOALS_AGAINST_BY_GAME]
			myAwayTempDic[CONST.TEAM_CLASSIFICATION]		= 'n/a'
			myAwayTempDic[CONST.TEAM_DEFENSE_RANKING]		= 'n/a'
			myAwayTempDic[CONST.TEAM_ATACK_RANKING]			= 'n/a'
			awayStatsDicTemp[gameAwayTeamKEY] 	= deepcopy(myAwayTempDic)


			# Total Stats
			for team_temp in [gameHomeTeamKEY,gameAwayTeamKEY]:
				homeStats 		= homeStatsDicTemp[team_temp] if team_temp in homeStatsDicTemp else {}
				awayStats 		= awayStatsDicTemp[team_temp] if team_temp in awayStatsDicTemp else {}

				teamID 			= team_temp.replace('%','.') + ' ' + champIDString

				totalTeamDic	= homeStats if CONST.TEAM_NAME in homeStats else awayStats

				homeGames 		= homeStats[CONST.TEAM_GAMES] if CONST.TEAM_GAMES in homeStats else 0
				awayGames 		= awayStats[CONST.TEAM_GAMES] if CONST.TEAM_GAMES in awayStats else 0
				totalgames 		= homeGames + awayGames

				homeGoalsFr		= homeStats[CONST.TEAM_GOALS_FOR] if CONST.TEAM_GOALS_FOR in homeStats else 0
				awayGoalsFr		= awayStats[CONST.TEAM_GOALS_FOR] if CONST.TEAM_GOALS_FOR in awayStats else 0
				totalGoalsFr 	= homeGoalsFr + awayGoalsFr


				homeGoalsAg		= homeStats[CONST.TEAM_GOALS_AGAINST] if CONST.TEAM_GOALS_AGAINST in homeStats else 0
				awayGoalsAg		= awayStats[CONST.TEAM_GOALS_AGAINST] if CONST.TEAM_GOALS_AGAINST in awayStats else 0
				totalGoalsAg 	= homeGoalsAg + awayGoalsAg

				homePoints 		= homeStats[CONST.TEAM_POINTS] if CONST.TEAM_POINTS in homeStats else 0
				awayPoints 		= awayStats[CONST.TEAM_POINTS] if CONST.TEAM_POINTS in awayStats else 0
				totalPoints		= homePoints + awayPoints

				totalGoalDif	= totalGoalsFr	- totalGoalsAg
				totalForm		= (totalPoints)	/ float(totalgames * 3)


				homeWins 			= homeStats[CONST.TEAM_WINS]			if CONST.TEAM_WINS			in homeStats else 0
				awayWins 			= awayStats[CONST.TEAM_WINS] 			if CONST.TEAM_WINS			in awayStats else 0
				homeDraws 			= homeStats[CONST.TEAM_DRAWS]			if CONST.TEAM_DRAWS			in homeStats else 0
				awayDraws 			= awayStats[CONST.TEAM_DRAWS] 			if CONST.TEAM_DRAWS			in awayStats else 0
				homeLoses 			= homeStats[CONST.TEAM_LOSES]			if CONST.TEAM_LOSES			in homeStats else 0
				awayLoses 			= awayStats[CONST.TEAM_LOSES] 			if CONST.TEAM_LOSES			in awayStats else 0
				homePoints 			= homeStats[CONST.TEAM_POINTS]			if CONST.TEAM_POINTS		in homeStats else 0
				awayPoints 			= awayStats[CONST.TEAM_POINTS] 			if CONST.TEAM_POINTS		in awayStats else 0
				homeScoreFirst 		= homeStats[CONST.TEAM_SCORE_FIRST]		if CONST.TEAM_SCORE_FIRST	in homeStats else 0
				awayScoreFirst 		= awayStats[CONST.TEAM_SCORE_FIRST] 	if CONST.TEAM_SCORE_FIRST	in awayStats else 0
				homeConseadFirst	= homeStats[CONST.TEAM_CONSEAD_FIRST]	if CONST.TEAM_CONSEAD_FIRST	in homeStats else 0
				awayConseadFirst	= awayStats[CONST.TEAM_CONSEAD_FIRST]	if CONST.TEAM_CONSEAD_FIRST	in awayStats else 0
				homeNoGoals 		= homeStats[CONST.TEAM_NO_GOALS]		if CONST.TEAM_NO_GOALS		in homeStats else 0
				awayNoGoals 		= awayStats[CONST.TEAM_NO_GOALS] 		if CONST.TEAM_NO_GOALS		in awayStats else 0
				homeUnder15 		= homeStats[CONST.TEAM_UNDER_15]		if CONST.TEAM_UNDER_15		in homeStats else 0
				awayUnder15 		= awayStats[CONST.TEAM_UNDER_15]		if CONST.TEAM_UNDER_15		in awayStats else 0
				homeOver15 			= homeStats[CONST.TEAM_OVER_15]			if CONST.TEAM_OVER_15		in homeStats else 0
				awayOver15 			= awayStats[CONST.TEAM_OVER_15] 		if CONST.TEAM_OVER_15		in awayStats else 0
				homeUnder25 		= homeStats[CONST.TEAM_UNDER_25]		if CONST.TEAM_UNDER_25		in homeStats else 0
				awayUnder25 		= awayStats[CONST.TEAM_UNDER_25] 		if CONST.TEAM_UNDER_25		in awayStats else 0
				homeOver25 			= homeStats[CONST.TEAM_OVER_25]			if CONST.TEAM_OVER_25		in homeStats else 0
				awayOver25 			= awayStats[CONST.TEAM_OVER_25] 		if CONST.TEAM_OVER_25		in awayStats else 0
				homeUnder35 		= homeStats[CONST.TEAM_UNDER_35]		if CONST.TEAM_UNDER_35		in homeStats else 0
				awayUnder35 		= awayStats[CONST.TEAM_UNDER_35] 		if CONST.TEAM_UNDER_35		in awayStats else 0
				homeOver35 			= homeStats[CONST.TEAM_OVER_35]			if CONST.TEAM_OVER_35		in homeStats else 0
				awayOver35 			= awayStats[CONST.TEAM_OVER_35] 		if CONST.TEAM_OVER_35		in awayStats else 0




				myTotalTempDic = {}
				myTotalTempDic[CONST.TEAM_LEAGUE]					= totalTeamDic[CONST.TEAM_LEAGUE]
				myTotalTempDic[CONST.TEAM_ID]						= teamID
				myTotalTempDic[CONST.TEAM_GAMES]                	= totalgames
				myTotalTempDic[CONST.TEAM_GOALS_FOR]            	= totalGoalsFr
				myTotalTempDic[CONST.TEAM_GOALS_AGAINST]        	= totalGoalsAg
				myTotalTempDic[CONST.TEAM_GOALS_DIF]            	= totalGoalDif
				myTotalTempDic[CONST.TEAM_FORM]                 	= totalForm
				myTotalTempDic[CONST.TEAM_NAME]                 	= totalTeamDic[CONST.TEAM_NAME]
				# myTotalTempDic[CONST.TEAM_LOGO]						= totalTeamDic[CONST.TEAM_LOGO]
				myTotalTempDic[CONST.TEAM_SHIRT_HOME]				= homeStats[CONST.TEAM_SHIRT_HOME] 	if CONST.TEAM_SHIRT_HOME in homeStats else ''
				myTotalTempDic[CONST.TEAM_SHIRT_AWAY]				= awayStats[CONST.TEAM_SHIRT_AWAY] 	if CONST.TEAM_SHIRT_AWAY in awayStats else ''
				myTotalTempDic[CONST.TEAM_MANAGER]					= totalTeamDic[CONST.TEAM_MANAGER]

				if team_temp == gameHomeTeamKEY:
					myTotalTempDic[CONST.TEAM_STADIUM]	= homeStats[CONST.TEAM_STADIUM]

				myTotalTempDic[CONST.TEAM_WINS]                 	= homeWins			+ awayWins
				myTotalTempDic[CONST.TEAM_DRAWS]                	= homeDraws			+ awayDraws
				myTotalTempDic[CONST.TEAM_LOSES]                	= homeLoses			+ awayLoses
				myTotalTempDic[CONST.TEAM_POINTS]               	= homePoints		+ awayPoints
				myTotalTempDic[CONST.TEAM_SCORE_FIRST]          	= homeScoreFirst	+ awayScoreFirst
				myTotalTempDic[CONST.TEAM_CONSEAD_FIRST]        	= homeConseadFirst 	+ awayConseadFirst
				myTotalTempDic[CONST.TEAM_NO_GOALS]             	= homeNoGoals 		+ awayNoGoals
				myTotalTempDic[CONST.TEAM_UNDER_15]             	= homeUnder15 		+ awayUnder15
				myTotalTempDic[CONST.TEAM_OVER_15]              	= homeOver15		+ awayOver15
				myTotalTempDic[CONST.TEAM_UNDER_25]             	= homeUnder25 		+ awayUnder25
				myTotalTempDic[CONST.TEAM_OVER_25]              	= homeOver25		+ awayOver25
				myTotalTempDic[CONST.TEAM_UNDER_35]             	= homeUnder35 		+ awayUnder35
				myTotalTempDic[CONST.TEAM_OVER_35]              	= homeOver35		+ awayOver35
				myTotalTempDic[CONST.TEAM_GOALS_FOR_BY_GAME]    	= totalGoalsFr									/ float(totalgames)
				myTotalTempDic[CONST.TEAM_GOALS_AGAINST_BY_GAME]	= totalGoalsAg									/ float(totalgames)
				myTotalTempDic[CONST.TEAM_GOALS_BY_GAME]        	= (totalGoalsFr + totalGoalsAg)					/ float(totalgames)
				myTotalTempDic[CONST.TEAM_SCORE_FIRST_BY_GAME]  	= myTotalTempDic[CONST.TEAM_SCORE_FIRST]		/ float(totalgames)
				myTotalTempDic[CONST.TEAM_CONSEAD_FIRST_BY_GAME]	= myTotalTempDic[CONST.TEAM_CONSEAD_FIRST]		/ float(totalgames)
				myTotalTempDic[CONST.TEAM_NO_GOALS_BY_GAME]     	= myTotalTempDic[CONST.TEAM_NO_GOALS]			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_UNDER_15_BY_GAME]     	= myTotalTempDic[CONST.TEAM_UNDER_15]			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_OVER_15_BY_GAME]      	= myTotalTempDic[CONST.TEAM_OVER_15] 			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_UNDER_25_BY_GAME]     	= myTotalTempDic[CONST.TEAM_UNDER_25]			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_OVER_25_BY_GAME]      	= myTotalTempDic[CONST.TEAM_OVER_25] 			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_UNDER_35_BY_GAME]     	= myTotalTempDic[CONST.TEAM_UNDER_35]			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_OVER_35_BY_GAME]      	= myTotalTempDic[CONST.TEAM_OVER_35] 			/ float(totalgames)
				myTotalTempDic[CONST.TEAM_CLASSIFICATION]       	= 'n/a'
				myTotalTempDic[CONST.TEAM_DEFENSE_RANKING]      	= 'n/a'
				myTotalTempDic[CONST.TEAM_ATACK_RANKING]        	= 'n/a'
				totalStatsDicTemp[team_temp] = deepcopy(myTotalTempDic)

			# Ratings calculation
			homeRankings	= __get_rankings__(homeStatsDicTemp)
			awayRankings	= __get_rankings__(awayStatsDicTemp)
			totalRankings 	= __get_rankings__(totalStatsDicTemp)
			for team in homeStatsDicTemp:
				homeStatsDicTemp[team][CONST.TEAM_CLASSIFICATION]	= homeRankings[CONST.TEAM_CLASSIFICATION][team]
				homeStatsDicTemp[team][CONST.TEAM_DEFENSE_RANKING]	= homeRankings[CONST.TEAM_DEFENSE_RANKING][team]
				homeStatsDicTemp[team][CONST.TEAM_ATACK_RANKING]	= homeRankings[CONST.TEAM_ATACK_RANKING][team]
			for team in awayStatsDicTemp:
				awayStatsDicTemp[team][CONST.TEAM_CLASSIFICATION]	= awayRankings[CONST.TEAM_CLASSIFICATION][team]
				awayStatsDicTemp[team][CONST.TEAM_DEFENSE_RANKING]	= awayRankings[CONST.TEAM_DEFENSE_RANKING][team]
				awayStatsDicTemp[team][CONST.TEAM_ATACK_RANKING]	= awayRankings[CONST.TEAM_ATACK_RANKING][team]
			for team in totalStatsDicTemp:
				totalStatsDicTemp[team][CONST.TEAM_CLASSIFICATION]	= totalRankings[CONST.TEAM_CLASSIFICATION][team]
				totalStatsDicTemp[team][CONST.TEAM_DEFENSE_RANKING]	= totalRankings[CONST.TEAM_DEFENSE_RANKING][team]
				totalStatsDicTemp[team][CONST.TEAM_ATACK_RANKING]	= totalRankings[CONST.TEAM_ATACK_RANKING][team]

			# FINAL ROUND STATS DIC!!!
			fixturesStatsDic[CONST.FIXTURES_STATS_GAME_NUMBER_ID]	= gameNumber
			fixturesStatsDic[CONST.FIXTURES_STATS_HOME_STATS] 		= homeStatsDicTemp
			fixturesStatsDic[CONST.FIXTURES_STATS_AWAY_STATS] 		= awayStatsDicTemp
			fixturesStatsDic[CONST.FIXTURES_STATS_TOTAL_STATS] 		= totalStatsDicTemp
			fixturesStatsDic[CONST.FIXTURES_STATS_BF_GAME_ID]		= game[CONST.GAME_ID]
			fixturesStatsDic[CONST.FIXTURES_STATS_LAST_GAME_INFO]	= game
			fullFixturesSimulatorStatsArr.append(deepcopy(fixturesStatsDic))

			#serverUtils.pprint(fullFixturesSimulatorStatsArr)

		# save to local simulator file
		readWriteToDisk.writeJsonData(fullFixturesSimulatorStatsArr, serverUtils.getLocalSimulatorStatsJsonFilePath(champID))
		
		# save to local stats file
		lastStats = deepcopy(fullFixturesSimulatorStatsArr[-1])
		lastStats.pop(CONST.FIXTURES_STATS_GAME_NUMBER_ID, None)
		lastStats.pop(CONST.FIXTURES_STATS_BF_GAME_ID	, None)
		lastStats.pop(CONST.FIXTURES_STATS_LAST_GAME_INFO, None)
		readWriteToDisk.writeJsonData(lastStats, serverUtils.getLocalStatsJsonFilePath(champID)) 

		# break
	return calcLog


'''
#######################################################################################
								Stats_db_Update
#######################################################################################
'''
def __start_Stats_db_Update__():
	log = []

	if len(championshipsIdsToUploadDropbox) == 0:
		tempLog = 'Noting Changed! All Files are updated.'
		log.append(tempLog)
		print (tempLog)
		return log

	finalStatsByChampDict = {}

	for champID in championshipsIdsToUploadDropbox: #serverUtils.getChampionshipsIdsList():
		champIDString = str(champID)
		champIDName = serverUtils.getChampionshipsNameFromID(champID)
		tempLog = 'Extracting data from: ' + serverUtils.getChampionshipsNameFromID(champID) + ' - ID: ' + champIDString
		log.append(tempLog)
		print (tempLog)
		
		# read local stats file
		statsFromLastGameFromDisk = serverUtils.getStatsFilefromDisk(champID)

		finalStatsByTeamDict = {}
		# get teams names and create dict
		for team in statsFromLastGameFromDisk[CONST.FIXTURES_STATS_TOTAL_STATS]:
			homeStats 	= statsFromLastGameFromDisk[CONST.FIXTURES_STATS_HOME_STATS][team]
			awayStats 	= statsFromLastGameFromDisk[CONST.FIXTURES_STATS_AWAY_STATS][team]
			totalStats 	= statsFromLastGameFromDisk[CONST.FIXTURES_STATS_TOTAL_STATS][team]
			teamLogo 	= statsFromLastGameFromDisk[CONST.FIXTURES_STATS_HOME_STATS][team][CONST.TEAM_LOGO]

			if team not in finalStatsByTeamDict:
				finalStatsByTeamDict[team] = {	
												CONST.DB_TEAM_HOME_STATS		: homeStats,
												CONST.DB_TEAM_AWAY_STATS		: awayStats,
												CONST.DB_TEAM_TOTAL_STATS		: totalStats,
												CONST.DB_TEAM_LOGO				: teamLogo
											}
			else:
				raise ValueError('ERROR: Team already exist!! maybe there is a team with the same name? -> team:', team, ' champID:', champIDString)


			finalStatsByChampDict[champIDName] = deepcopy(finalStatsByTeamDict)
			# break

		# break

	#save stats db to local file
	readWriteToDisk.writeJsonData(finalStatsByChampDict, serverUtils.getLocalDbJsonFilePath())
	return log
		

'''
#######################################################################################
								 	Tips
#######################################################################################
'''
def __start_Tips_db_Update__():
	log = []

	if len(championshipsIdsToUploadDropbox) == 0:
		tempLog = 'Noting Changed! All Files are updated.'
		log.append(tempLog)
		print (tempLog)
		return log

	dbLocalFile = serverUtils.getDbFilefromDisk()

	FinalTipsDB = {}

	for champID in serverUtils.getChampionshipsIdsList():
		champIDString = str(champID)
		champName = serverUtils.getChampionshipsNameFromID(champID)
		tempLog = 'Extracting data from: ' + serverUtils.getChampionshipsNameFromID(champID) + ' - ID: ' + champIDString
		log.append(tempLog)
		print (tempLog)
		
		# read local crawler file
		filefromDisk = serverUtils.getCrawlerFilefromDisk(champID)

		futureGames = [game for game in filefromDisk if game[CONST.GAME_FT_SCORE] == '']

		if len(futureGames) == 0:
			print (champName, '- No shedules games! League finished? - SKIPING...')
			continue

		futureGamesSorted 	= sorted(futureGames, key=lambda k: k[CONST.GAME_DATE_TO_SORT])
		tempTeamsArr 		= []
		nextGames 			= []	
		for game in futureGamesSorted:
			if game[CONST.GAME_HOME_TEAM] not in tempTeamsArr and game[CONST.GAME_AWAY_TEAM] not in tempTeamsArr:
				tempTeamsArr.append(game[CONST.GAME_HOME_TEAM])
				tempTeamsArr.append(game[CONST.GAME_AWAY_TEAM])
				nextGames.append(game)
			else:
				break

		nextGamesSorted	= sorted(nextGames, key=lambda k: k[CONST.GAME_DATE_TO_SORT])
		nextGamesTips = []
		for game in nextGamesSorted:
			homeTeam = game[CONST.GAME_HOME_TEAM]
			awayTeam = game[CONST.GAME_AWAY_TEAM]
			allTips = tips.getTips(homeTeam,awayTeam,dbLocalFile[champName])

			gameTips = game.copy()
			gameTips.pop(CONST.GAME_FT_SCORE, None)
			gameTips.pop(CONST.GAME_HF_SCORE, None)
			gameTips.pop(CONST.GAME_CHAMPIONSHIP_ID, None)
			gameTips[CONST.TIPS_ALL] = allTips

			nextGamesTips.append(gameTips)

		FinalTipsDB[champName] = nextGamesTips


	#save tips db to local file
	readWriteToDisk.writeJsonData(FinalTipsDB, serverUtils.getLocalTipsJsonFilePath())
	return log


'''
#######################################################################################
								Leagues_To_Trade
#######################################################################################
'''
def __get_All_Ready_Leagues_To_Trade__():
	if len(championshipsIdsToUploadDropbox) == 0:
		log = []
		tempLog = 'Noting Changed! All Files are updated.'
		log.append(tempLog)
		print (tempLog)
		return log

	# load db file
	dbData = readWriteToDisk.readJsonData(serverUtils.getLocalDbJsonFilePath())

	leguesReadyDic = {}
	for championshipID in serverUtils.getChampionshipsIdsList():
		champName = serverUtils.getChampionshipsNameFromID(championshipID)
		dbDataOfChamp = dbData[champName]


		# Testing if the champ is over...
		filefromDisk = serverUtils.getCrawlerFilefromDisk(championshipID)
		futureGames = [game for game in filefromDisk if game[CONST.GAME_FT_SCORE] == '']
		if len(futureGames) == 0:
			# print champName, '- No shedules games! League finished? - SKIPING...'
			continue


		# Count championship teams
		teamsInChampionship = []
		gamescount = 0
		for team in dbDataOfChamp.keys():
			teamsInChampionship.append(team)
			gamescount += dbDataOfChamp[team][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_GAMES]

		teamsCount = len(teamsInChampionship)
		minGames = int(teamsCount)/2 * 10
		playedGames = gamescount/2
		ready = 'not Ready' if playedGames < minGames else '>>>> Ready! <<<<'

		leagueInfo = {
			'teams' 		: teamsCount,
			'min Games' 	: minGames,
			'played Games' 	: playedGames,
			'trade' 		: ready
		}
		leguesReadyDic[serverUtils.getChampionshipsNameFromID(championshipID)] = leagueInfo
		readyInfo = ' (' + str(playedGames) + '/' + str(minGames) + ')'
		serverUtils.pprint(serverUtils.getChampionshipsNameFromID(championshipID) + ': ' + ready + readyInfo)

	return leguesReadyDic


'''
#######################################################################################
							sendRestServerNotification
#######################################################################################
'''
def __sendRestServerNotification__():
	log = []

	if len(championshipsIdsToUploadDropbox) == 0:
		tempLog = 'Noting Changed! All Files are updated.'
		log.append(tempLog)
		print (tempLog)
		return log

	updateFileReq = requests.post(
									'https://127.0.0.1/update/', 
									'updateFile', 
									verify 	= False, 
									auth 	= HTTPBasicAuth('user', 'pass')
								)
	try:
		resp = serverUtils.jsonImport(updateFileReq.content)
		log.append(resp)
		serverUtils.pprint(resp)
	except Exception as e:
		tempLog=  'sendRestServerNotification err: ' + updateFileReq.content
		log.append(tempLog)
		serverUtils.pprint(tempLog)
	return log



'''
#######################################################################################
								uploadFilesToDropbox
#######################################################################################
'''
def __uploadFilesToDropbox__():
	log = []
	if len(championshipsIdsToUploadDropbox) == 0:
		tempLog = 'Noting to upload! All Files are updated.'
		log.append(tempLog)
		print (tempLog)
		return log

	for championshipID in championshipsIdsToUploadDropbox:
		# upload crawler file to Dropbox
		filefrom 	= serverUtils.getLocalCrawlerJsonFilePath(championshipID)
		fileTo 		= serverUtils.getDropboxCrawlerJsonFilePath(championshipID)
		try:
			dropboxAPI.uploadToDropbox(filefrom, fileTo)
			tempLog = 'Done uploading crawler Json file for championshipID: ' + str(championshipID)
			log.append(tempLog)
			print (tempLog)
		except Exception as e:
			error = 'ERROR uploading crawler Json file for championshipID: ' + str(championshipID) + ' - ' + str(e)
			log.append(error)
			print (error)
			
		# upload stats file to Dropbox (NOT RECOMMENDED!!! LARGE FILES!)
		# filefrom 	= serverUtils.getLocalStatsJsonFilePath(championshipID)
		# fileTo 		= serverUtils.getDropboxStatsJsonFilePath(championshipID)
		# try:
		# 	dropboxAPI.uploadToDropbox(filefrom, fileTo)
		# 	tempLog = 'Done uploading stats Json file for championshipID: ' + str(championshipID)
		# 	log.append(tempLog)
		# 	print (tempLog)
		# except Exception as e:
		# 	error = 'ERROR uploading stats Json file for championshipID: ' + str(championshipID) + ' - ' + str(e)
		# 	log.append(error)
		# 	print error


	# upload finalDB file to Dropbox
	filefrom 	= serverUtils.getLocalDbJsonFilePath()
	fileTo 		= serverUtils.getDropboxDbJsonFilePath()
	try:
		dropboxAPI.uploadToDropbox(filefrom, fileTo)
		tempLog = 'Done uploading finalDB Json file'
		log.append(tempLog)
		print (tempLog)
	except Exception as e:
		error = 'ERROR uploading finalDB Json file - ' + str(e)
		log.append(error)
		print (error)


	# upload Tips db file to Dropbox
	filefrom 	= serverUtils.getLocalTipsJsonFilePath()
	fileTo 		= serverUtils.getDropboxTipsJsonFilePath()
	try:
		dropboxAPI.uploadToDropbox(filefrom, fileTo)
		tempLog = 'Done uploading Tips Json file'
		log.append(tempLog)
		print (tempLog)
	except Exception as e:
		error = 'ERROR uploading Tips Json file - ' + str(e)
		log.append(error)
		print (error)

	return log









def start():
	updateStartTime = time.time()
	crawlerLog 		= []
	calcLog 		= []
	dbLog 			= []
	tipsLog 		= []
	leaguesReadyLog = []
	dropboxLog 		= []
	mailLog 		= []
	restServerLog 	= []


	try:
		print ('##########################__startCrawler__##########################')
		crawlerLog = __startCrawler__()
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		crawlerLog = tempLog
		print (tempLog)
		
	

	try:
		print (' ')
		print ('#################__start_RoundsStats_Calculations__#################')
		calcLog = __start_RoundsStats_Calculations__()
	except Exception as err:
		tempLog = ['ERROR: ' + str(err), err]
		calcLog = tempLog
		print (tempLog)
	

	try:
		print (' ')
		print ('#####################__start_Stats_db_Update__######################')
		dbLog = __start_Stats_db_Update__()
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		dbLog = tempLog
		print (tempLog)


	try:
		print (' ')
		print ('#####################__start_Tips_db_Update__#######################')
		tipsLog = __start_Tips_db_Update__()
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		tipsLog = tempLog

		print (tempLog)

	try:
		print (' ')
		print ('#################__get_All_Ready_Leagues_To_Trade__#################')
		leaguesReadyLog = __get_All_Ready_Leagues_To_Trade__()
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		leaguesReadyLog = tempLog
		print (tempLog)
	
	try:
		print (' ')
		print ('##################__sendRestServerNotification__####################')
		restServerLog = __sendRestServerNotification__()
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		restServerLog = tempLog
		print (tempLog)

	try:
		print (' ')
		print ('#####################__uploadFilesToDropbox__#######################')
		dropboxLog = __uploadFilesToDropbox__()
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		dropboxLog = tempLog
		print (tempLog)

	try:
		print (' ')
		print ('############################__mailLogs__############################')
		updateEndTime = time.time()
		totalTime = str(datetime.timedelta(seconds=int(updateEndTime-updateStartTime)))
		dataToSendByEmail = [
								{'Update Date' 					: time.ctime(), 'Update Duration' : totalTime},
								{'Crawler Log' 					: crawlerLog},
								{'Calculations Log' 			: calcLog},
								{'db Update Log' 				: dbLog},
								{'tips Log'						: tipsLog},
								{'Leagues Ready for Trade Log' 	: leaguesReadyLog},
								{'Rest Server Notification Log'	: restServerLog},
								{'Dropbox Upload Log' 			: dropboxLog}
							]
		mailLog = sendServerEmail.sendServerEmail(dataToSendByEmail)
		print (mailLog)
	except Exception as err:
		tempLog = 'ERROR: ' + str(err)
		mailLog = tempLog
		print (tempLog)

	print (' ')
	print ('#########################__All Work Done__##########################')


if __name__ == '__main__':
	# executed as script
	# xvfb-run -a python /mnt/smb/py.py

	championshipsIdsToUploadDropbox = serverUtils.getChampionshipsIdsList()#[]
	
	debug = False
	
	if not debug:
		print (' ')
		print ('Starting Update...')
		print (' ')
		start()
	else:
		print (' ')
		print ('Starting Update...        DEBUG=True')
		championshipsIdsToUploadDropbox = serverUtils.getChampionshipsIdsList()

		print (' ')
		print ('##########################__startCrawler__##########################')
		__startCrawler__()
		print (' ')
		print ('#################__start_RoundsStats_Calculations__#################')
		__start_RoundsStats_Calculations__()
		print (' ')
		print ('#####################__start_Stats_db_Update__######################')
		__start_Stats_db_Update__()
		print (' ')
		print ('#####################__start_Tips_db_Update__#######################')
		__start_Tips_db_Update__()
		print (' ')
		print ('#################__get_All_Ready_Leagues_To_Trade__#################')
		__get_All_Ready_Leagues_To_Trade__()


		# print (' ')
		# print ('##################__sendRestServerNotification__####################')
		# __sendRestServerNotification__()


		# print (' ')
		# print ('#####################__uploadFilesToDropbox__#######################')
		# print ('DEBUG=True -> Forcing all files to be updated!')
		# __uploadFilesToDropbox__()


		# print (' ')
		# print ('############################__mailLogs__############################')
		#sendServerEmail.sendServerEmail(["db Update done: DEBUG=True"])

		
		print (' ')
		print ('#########################__All Work Done__##########################')







