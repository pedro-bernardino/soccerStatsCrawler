# coding=utf-8
import serverUtils
import serverConstants as CONST
import tips

def start():
	for champID in serverUtils.getChampionshipsIdsList():	#get championships used from the db
		champName = serverUtils.getChampionshipsNameFromID(champID)
		# get Simulator file
		champSimulatorFile = serverUtils.getSimulatorFilefromDisk(champID)
		if not len(champSimulatorFile) > 0:
			print ('Skiping:', champName, 'File empty!')
			continue


		# teams count
		teamsCount 	= len(champSimulatorFile[-1][CONST.FIXTURES_STATS_TOTAL_STATS])
		gamesPerRound 	= teamsCount / 2
		gameNumber 		= (gamesPerRound * 10) + 1 #round 10 game number

		fullResultDict = 	{	CONST.TIP_15_GOALS 				: {True : 0, False : 0},
								CONST.TIP_25_GOALS 				: {True : 0, False : 0},
								CONST.TIP_35_GOALS 				: {True : 0, False : 0},
								CONST.POISSON_TIPS 				: {True : 0, False : 0},
								CONST.BIVARIATE_POISSON_TIPS	: {True : 0, False : 0},
							}
		for i in xrange(gameNumber, len(champSimulatorFile)):
			# After Game Info
			gameInfo 		= champSimulatorFile[i][CONST.FIXTURES_STATS_LAST_GAME_INFO]
			homeTeamName 	= gameInfo[CONST.GAME_HOME_TEAM]
			awayTeamName 	= gameInfo[CONST.GAME_AWAY_TEAM]
			gameFTScore		= gameInfo[CONST.GAME_FT_SCORE]
			goalsARR		= gameInfo[CONST.GAME_FT_SCORE].split('-')
			goalsSUM 		= int(goalsARR[0]) + int(goalsARR[1])

			# Before Game Stats
			beforeGameHometeamHomeStats 	= champSimulatorFile[i-1][CONST.FIXTURES_STATS_HOME_STATS][homeTeamName]
			beforeGameHometeamAwayStats 	= champSimulatorFile[i-1][CONST.FIXTURES_STATS_AWAY_STATS][homeTeamName]
			beforeGameHometeamTotalStats 	= champSimulatorFile[i-1][CONST.FIXTURES_STATS_TOTAL_STATS][homeTeamName]
			beforeGameAwayteamHomeStats 	= champSimulatorFile[i-1][CONST.FIXTURES_STATS_HOME_STATS][awayTeamName]
			beforeGameAwayteamAwayStats 	= champSimulatorFile[i-1][CONST.FIXTURES_STATS_AWAY_STATS][awayTeamName]
			beforeGameAwayteamTotalStats 	= champSimulatorFile[i-1][CONST.FIXTURES_STATS_TOTAL_STATS][awayTeamName]

			# Tips for Games
			tempDB = 	{ 	homeTeamName : 	{ 	CONST.DB_TEAM_HOME_STATS	: beforeGameHometeamHomeStats,
												CONST.DB_TEAM_AWAY_STATS 	: beforeGameHometeamAwayStats,
												CONST.DB_TEAM_TOTAL_STATS 	: beforeGameHometeamTotalStats,
											},
							awayTeamName : 	{ 	CONST.DB_TEAM_HOME_STATS	: beforeGameAwayteamHomeStats,
												CONST.DB_TEAM_AWAY_STATS 	: beforeGameAwayteamAwayStats,
												CONST.DB_TEAM_TOTAL_STATS 	: beforeGameAwayteamTotalStats,
											}
						}
			tipsCalculations 	= tips.getTips(homeTeamName,awayTeamName,tempDB) 



			# serverUtils.pprint(tipsCalculations)
			# serverUtils.pprint(gameInfo)

			tip15 = ''
			tip25 = ''
			tip35 = ''
			if goalsSUM < 2:
				tip15 = 'UNDER'
				tip25 = 'UNDER'
				tip35 = 'UNDER'
			elif goalsSUM < 3:
				tip15 = 'OVER'
				tip25 = 'UNDER'
				tip35 = 'UNDER'
			elif goalsSUM < 4:
				tip15 = 'OVER'
				tip25 = 'OVER'
				tip35 = 'UNDER'
			else:
				tip15 = 'OVER'
				tip25 = 'OVER'
				tip35 = 'UNDER'

			# result
			tip15Bool 	= tipsCalculations[CONST.GOALS_TIPS][CONST.TIP_15_GOALS] in (tip15, 'NO BET')
			tip25Bool 	= tipsCalculations[CONST.GOALS_TIPS][CONST.TIP_25_GOALS] in (tip25, 'NO BET')
			tip35Bool 	= tipsCalculations[CONST.GOALS_TIPS][CONST.TIP_35_GOALS] in (tip35, 'NO BET')
			poissonBool = gameFTScore.replace("-", ":") in tipsCalculations[CONST.POISSON_TIPS]
			bvPoisson 	= gameFTScore.replace("-", ":") in tipsCalculations[CONST.BIVARIATE_POISSON_TIPS]

			fullResultDict[CONST.TIP_15_GOALS][tip15Bool] 			+= 1
			fullResultDict[CONST.TIP_25_GOALS][tip25Bool] 			+= 1
			fullResultDict[CONST.TIP_35_GOALS][tip35Bool] 			+= 1
			fullResultDict[CONST.POISSON_TIPS][poissonBool] 		+= 1
			fullResultDict[CONST.BIVARIATE_POISSON_TIPS][bvPoisson] += 1

			# print CONST.TIP_15_GOALS + ':', tipsCalculations[CONST.GOALS_TIPS][CONST.TIP_15_GOALS] == tip15
			# print CONST.TIP_25_GOALS + ':', tipsCalculations[CONST.GOALS_TIPS][CONST.TIP_25_GOALS] == tip25
			# print CONST.TIP_35_GOALS + ':', tipsCalculations[CONST.GOALS_TIPS][CONST.TIP_35_GOALS] == tip35
			# print CONST.POISSON_TIPS 			+ ':', gameFTScore.replace("-", ":") in tipsCalculations[CONST.POISSON_TIPS]
			# print CONST.BIVARIATE_POISSON_TIPS 	+ ':', gameFTScore.replace("-", ":") in tipsCalculations[CONST.BIVARIATE_POISSON_TIPS]


			# break
		
		print (' ')
		print (champName)
		finalResults = 	{
							CONST.TIP_15_GOALS : round((fullResultDict[CONST.TIP_15_GOALS][True] / float(fullResultDict[CONST.TIP_15_GOALS][True] + fullResultDict[CONST.TIP_15_GOALS][False])) * 100, 2),
							CONST.TIP_25_GOALS : round((fullResultDict[CONST.TIP_25_GOALS][True] / float(fullResultDict[CONST.TIP_25_GOALS][True] + fullResultDict[CONST.TIP_25_GOALS][False])) * 100, 2),
							CONST.TIP_35_GOALS : round((fullResultDict[CONST.TIP_35_GOALS][True] / float(fullResultDict[CONST.TIP_35_GOALS][True] + fullResultDict[CONST.TIP_35_GOALS][False])) * 100, 2),
							CONST.POISSON_TIPS : round((fullResultDict[CONST.POISSON_TIPS][True] / float(fullResultDict[CONST.POISSON_TIPS][True] + fullResultDict[CONST.POISSON_TIPS][False])) * 100, 2),
							CONST.BIVARIATE_POISSON_TIPS : round((fullResultDict[CONST.BIVARIATE_POISSON_TIPS][True] / float(fullResultDict[CONST.BIVARIATE_POISSON_TIPS][True] + fullResultDict[CONST.BIVARIATE_POISSON_TIPS][False])) * 100, 2),
						}
		serverUtils.pprint(finalResults)
		# break

if __name__ == '__main__':
	start()