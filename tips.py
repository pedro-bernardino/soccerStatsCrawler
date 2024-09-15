# coding=utf-8
import math
import serverConstants as CONST
import serverUtils

def __scoresToStudy__():
    return ["0:0","0:1","0:2","0:3","0:4","0:5","0:6","0:7","0:8","0:9",
            "1:0","1:1","1:2","1:3","1:4","1:5","1:6","1:7","1:8","1:9",
            "2:0","2:1","2:2","2:3","2:4","2:5","2:6","2:7","2:8","2:9",
            "3:0","3:1","3:2","3:3","3:4","3:5","3:6","3:7","3:8","3:9",
            "4:0","4:1","4:2","4:3","4:4","4:5","4:6","4:7","4:8","4:9",
            "5:0","5:1","5:2","5:3","5:4","5:5","5:6","5:7","5:8","5:9",
            "6:0","6:1","6:2","6:3","6:4","6:5","6:6","6:7","6:8","6:9",
            "7:0","7:1","7:2","7:3","7:4","7:5","7:6","7:7","7:8","7:9",
            "8:0","8:1","8:2","8:3","8:4","8:5","8:6","8:7","8:8","8:9",
            "9:0","9:1","9:2","9:3","9:4","9:5","9:6","9:7","9:8","9:9"]

def __getExpectedGoalsOfHomeTeamAwayTeamwithStats__(hTeam, aTeam, statsDic):
    hometeamLeague  = statsDic[hTeam][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_LEAGUE]
    awayteamLeague  = statsDic[aTeam][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_LEAGUE]
    sumHomeTeams    = 0.0
    sumAwayTeams    = 0.0
    sumHomeGF       = 0.0
    sumAwayGF       = 0.0
    sumHomeGA       = 0.0
    sumAwayGA       = 0.0
    sumHomeGames    = 0.0
    sumAwayGames    = 0.0


    for teamKey in statsDic:
        tempTeamLeague = statsDic[teamKey][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_LEAGUE]
        if hometeamLeague == tempTeamLeague:
            sumHomeTeams    += 1
            sumHomeGF       += statsDic[teamKey][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_FOR]
            sumHomeGA       += statsDic[teamKey][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_AGAINST]
            sumHomeGames    += statsDic[teamKey][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GAMES]

        if awayteamLeague == tempTeamLeague:
            sumAwayTeams    += 1
            sumAwayGF       += statsDic[teamKey][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_FOR]
            sumAwayGA       += statsDic[teamKey][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_AGAINST]
            sumAwayGames    += statsDic[teamKey][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GAMES]

    homeGamesAverage = sumHomeGames / sumHomeTeams
    awayGamesAverage = sumAwayGames / sumAwayTeams
    
    homeGFAverage = sumHomeGF / sumHomeTeams
    awayGFAverage = sumAwayGF / sumAwayTeams
    homeGAAverage = sumHomeGA / sumHomeTeams
    awayGAAverage = sumAwayGA / sumAwayTeams
    leagueHomeGFAverage = homeGFAverage / homeGamesAverage
    leagueAwayGFAverage = awayGFAverage / awayGamesAverage
    
    # print 'homeGFAverage: '         + str(homeGFAverage)
    # print 'awayGFAverage: '         + str(awayGFAverage)
    # print 'homeGAAverage: '         + str(homeGAAverage)
    # print 'awayGAAverage: '         + str(awayGAAverage)
    # print 'leagueHomeGFAverage: '   + str(leagueHomeGFAverage)
    # print 'leagueAwayGFAverage: '   + str(leagueAwayGFAverage)


    homeTeamGF = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_FOR]
    awayTeamGF = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_FOR]
    homeTeamGA = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_AGAINST]
    awayTeamGA = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_AGAINST]
    
    homeTeamGFExpected = homeTeamGF / homeGFAverage
    awayTeamGFExpected = awayTeamGF / awayGFAverage
    homeTeamGAExpected = homeTeamGA / homeGAAverage
    awayTeamGAExpected = awayTeamGA / awayGAAverage
    
    homeExpectedGoals = homeTeamGFExpected * awayTeamGAExpected * leagueHomeGFAverage
    awayExpectedGoals = awayTeamGFExpected * homeTeamGAExpected * leagueAwayGFAverage
    
    result = [homeExpectedGoals, awayExpectedGoals]
    return result

def __getPoissonForGoalsWithExpectedGoals__(goals,expectedGoals):
    a1 = math.pow(expectedGoals, goals)
    a2 = math.exp(-expectedGoals)
    a3 = math.factorial(goals)
    prob = (a1 * a2) / a3
    
    return prob

def __getPoissonWithHomeExpectedGoalsAwayExpectedGoals__(homeGoals, awayGoals):
    biv = []
    a1 = []
    for j in xrange(10):
        a1.append( math.pow(CONST.COVARIANCE, j) / math.factorial(j) )
    for h in xrange(10):
    	for a in xrange(10):
            h1 = math.pow(homeGoals, h)
            h2 = math.exp(-homeGoals)
            h3 = math.factorial(h)
            probHome = (h1*h2)/h3
            
            a1 = math.pow(awayGoals, a)
            a2 = math.exp(-awayGoals)
            a3 = math.factorial(a)
            probAway = (a1*a2)/a3
            
            p = probHome * probAway
            biv.append(p)
    return biv

def __getBivariatePoissonWithHomeExpectedGoalsAwayExpectedGoals__(homeGoals, awayGoals):
    expp = math.exp(-1 * (homeGoals + awayGoals + CONST.COVARIANCE))
    biv2 = []
    
    for h in xrange(10):
        for a in xrange(10):
            m = 0
            if h > a:
                m = a
            elif a <= h:
                m = h

            s = 0
            for j in xrange(m+1):
                t1 = math.pow(CONST.COVARIANCE, j)  / math.factorial(j)
                t2 = math.pow(homeGoals, h - j)     / math.factorial(h - j)
                t3 = math.pow(awayGoals, a - j)     / math.factorial(a - j)
                s += t1 * t2 * t3
            p = expp * s
            biv2.append(p)
    return biv2

def __possibleScoreForHomeExpectedGoalsAwayExpectedGoals__(homeGoals, awayGoals):
    scores = __scoresToStudy__()
    poisson = __getPoissonWithHomeExpectedGoalsAwayExpectedGoals__(homeGoals, awayGoals)
    bvPoisson = __getBivariatePoissonWithHomeExpectedGoalsAwayExpectedGoals__(homeGoals, awayGoals)
    
    maxPoisson 		= max(poisson)
    maxBVPoisson 	= max(bvPoisson)
    maxPoissonPos 	= poisson.index(maxPoisson)
    maxBVPoissonPos = bvPoisson.index(maxBVPoisson)
    
    # remove max to find second max
    poissonTemp 		= list(poisson)   #duplicate list
    bvPoissonTemp 		= list(bvPoisson) #duplicate list
    poissonTemp.remove(maxPoisson)
    bvPoissonTemp.remove(maxBVPoisson)
    maxPoisson2 		= max(poissonTemp)
    maxBVPoisson2 		= max(bvPoissonTemp)
    maxPoissonPos2 		= poisson.index(maxPoisson2)
    maxBVPoissonPos2 	= bvPoisson.index(maxBVPoisson2)
    
    # remove second max to find third max
    poissonTemp.remove(maxPoisson2)
    bvPoissonTemp.remove(maxBVPoisson2)
    maxPoisson3 		= max(poissonTemp)
    maxBVPoisson3 		= max(bvPoissonTemp)
    maxPoissonPos3 		= poisson.index(maxPoisson3)
    maxBVPoissonPos3 	= bvPoisson.index(maxBVPoisson3)
    
    resultToReturn = [
    					[
    						scores[maxPoissonPos], 
    						maxPoisson,
               				scores[maxPoissonPos2], 
               				maxPoisson2,
               				scores[maxPoissonPos3], 
               				maxPoisson3
               			],
               			[
               				scores[maxBVPoissonPos], 
               				maxBVPoisson,
               				scores[maxBVPoissonPos2], 
               				maxBVPoisson2,
               				scores[maxBVPoissonPos3], 
               				maxBVPoisson3
               			]
               		]
    return resultToReturn

def __getGoalsTipOfHomeTeamAwayTeamWithStats__(hTeam, aTeam, statsDic):
    homeGames           = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GAMES]
    homeGF_Game         = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_FOR_BY_GAME]
    homeGA_Game         = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_AGAINST_BY_GAME]
    homeUnder15_Game    = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_UNDER_15_BY_GAME]
    homeOver15_Game     = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_OVER_15_BY_GAME]
    homeUnder25_Game    = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_UNDER_25_BY_GAME]
    homeOver25_Game     = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_OVER_25_BY_GAME]
    homeUnder35_Game    = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_UNDER_35_BY_GAME]
    homeOver35_Game     = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_OVER_35_BY_GAME]
    homeTeamGF          = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_FOR]
    homeTeamGA          = statsDic[hTeam][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_AGAINST]
    
    awayGF_Game         = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_FOR]
    awayGA_Game         = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_AGAINST_BY_GAME]
    awayUnder15_Game    = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_UNDER_15_BY_GAME]
    awayOver15_Game     = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_OVER_15_BY_GAME]
    awayUnder25_Game    = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_UNDER_25_BY_GAME]
    awayOver25_Game     = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_OVER_25_BY_GAME]
    awayUnder35_Game    = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_UNDER_35_BY_GAME]
    awayOver35_Game     = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_OVER_35_BY_GAME]
    awayTeamGF          = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_FOR]
    awayTeamGA          = statsDic[aTeam][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_AGAINST]
    
    # league total calculations
    hometeamLeague  = statsDic[hTeam][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_LEAGUE]
    awayteamLeague  = statsDic[aTeam][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_LEAGUE]
    sumHomeTeams    = 0.0
    sumAwayTeams    = 0.0
    sumHomeGF       = 0.0
    sumAwayGF       = 0.0
    sumHomeGA       = 0.0
    sumAwayGA       = 0.0
    sumHomeGames    = 0.0
    sumAwayGames    = 0.0


    for teamKey in statsDic:
        tempTeamLeague = statsDic[teamKey][CONST.DB_TEAM_TOTAL_STATS][CONST.TEAM_LEAGUE]
        if hometeamLeague == tempTeamLeague:
            sumHomeTeams    += 1
            sumHomeGF       += statsDic[teamKey][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_FOR]
            sumHomeGA       += statsDic[teamKey][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GOALS_AGAINST]
            sumHomeGames    += statsDic[teamKey][CONST.DB_TEAM_HOME_STATS][CONST.TEAM_GAMES]

        if awayteamLeague == tempTeamLeague:
            sumAwayTeams    += 1
            sumAwayGF       += statsDic[teamKey][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_FOR]
            sumAwayGA       += statsDic[teamKey][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GOALS_AGAINST]
            sumAwayGames    += statsDic[teamKey][CONST.DB_TEAM_AWAY_STATS][CONST.TEAM_GAMES]

    homeGamesAverage = sumHomeGames / sumHomeTeams
    awayGamesAverage = sumAwayGames / sumAwayTeams
    
    homeGFAverage = sumHomeGF / sumHomeTeams
    awayGFAverage = sumAwayGF / sumAwayTeams
    homeGAAverage = sumHomeGA / sumHomeTeams
    awayGAAverage = sumAwayGA / sumAwayTeams
    
    homeTeamAttack   = homeTeamGF / homeGFAverage
    awayTeamAttack   = awayTeamGF / awayGFAverage
    homeTeamDefence  = homeTeamGA / homeGAAverage
    awayTeamDefence  = awayTeamGA / awayGAAverage
    

    # Tips calculations
    probUnder15DEN      = (homeUnder15_Game * awayUnder15_Game + homeOver15_Game * awayOver15_Game)
    probUnder25DEN      = (homeUnder25_Game * awayUnder25_Game + homeOver25_Game * awayOver25_Game)
    probUnder35DEN      = (homeUnder35_Game * awayUnder35_Game + homeOver35_Game * awayOver35_Game)
    probabilityUnder15  = (homeUnder15_Game * awayUnder15_Game) / probUnder15DEN if probUnder15DEN > 0 else (homeUnder15_Game * awayUnder15_Game)
    probabilityUnder25  = (homeUnder25_Game * awayUnder25_Game) / probUnder25DEN if probUnder25DEN > 0 else (homeUnder25_Game * awayUnder25_Game)
    probabilityUnder35  = (homeUnder35_Game * awayUnder35_Game) / probUnder35DEN if probUnder35DEN > 0 else (homeUnder35_Game * awayUnder35_Game)
    probabilityOver15    = 1 - probabilityUnder15
    probabilityOver25    = 1 - probabilityUnder25
    probabilityOver35    = 1 - probabilityUnder35
    
    expected15Goals1      = 1 * probabilityUnder15 + 2 * probabilityOver15
    expected25Goals1      = 2 * probabilityUnder25 + 3 * probabilityOver25
    expected35Goals1      = 3 * probabilityUnder35 + 4 * probabilityOver35

    expectedHomeGoals      = homeTeamAttack * homeGF_Game * awayTeamDefence
    expectedAwayGoals      = awayTeamAttack * awayGF_Game * homeTeamDefence
    expectedGoalsFinal     = (expectedHomeGoals + expectedAwayGoals) / 2
    
    expectedGoals          = __getExpectedGoalsOfHomeTeamAwayTeamwithStats__(hTeam, aTeam, statsDic)

    expectedHomeGoals2     = expectedGoals[0]
    expectedAwayGoals2     = expectedGoals[1]
    expectedGoalsFinal2    = (expectedHomeGoals2 + expectedAwayGoals2) / 2

    expected15GoalsFinal   = (expected15Goals1 + expectedGoalsFinal + expectedGoalsFinal2) / 3.0
    expected25GoalsFinal   = (expected25Goals1 + expectedGoalsFinal + expectedGoalsFinal2) / 3.0
    expected35GoalsFinal   = (expected35Goals1 + expectedGoalsFinal + expectedGoalsFinal2) / 3.0
    
    tip15 = 'Error'
    tip25 = 'Error'
    tip35 = 'Error'

    if expected15GoalsFinal < (1.5 - CONST.TIP_UNDER_COEFICIENTE):
        tip15 = "UNDER"
    elif expected15GoalsFinal > (1.5 + CONST.TIP_OVER_COEFICIENTE):
        tip15 = "OVER"
    else:
        tip15 = "NO BET"

    if expected25GoalsFinal < (2.5 - CONST.TIP_UNDER_COEFICIENTE):
        tip25 = "UNDER"
    elif expected25GoalsFinal > (2.5 + CONST.TIP_OVER_COEFICIENTE):
        tip25 = "OVER"
    else:
        tip25 = "NO BET"

    if expected35GoalsFinal < (3.5 - CONST.TIP_UNDER_COEFICIENTE):
        tip35 = "UNDER"
    elif expected35GoalsFinal > (3.5 + CONST.TIP_OVER_COEFICIENTE):
        tip35 = "OVER"
    else:
        tip35 = "NO BET"

    result = {
                CONST.PROBABILITY_UNDER_15    : probabilityUnder15,
                CONST.PROBABILITY_OVER_15     : probabilityOver15,
                CONST.PROBABILITY_UNDER_25    : probabilityUnder25,
                CONST.PROBABILITY_OVER_25     : probabilityOver25,
                CONST.PROBABILITY_UNDER_35    : probabilityUnder35,
                CONST.PROBABILITY_OVER_35     : probabilityOver35,
                CONST.EXPECTED_GOALS_15       : expected15GoalsFinal,
                CONST.EXPECTED_GOALS_25       : expected25GoalsFinal,
                CONST.EXPECTED_GOALS_35       : expected35GoalsFinal,
                CONST.TIP_15_GOALS            : tip15,
                CONST.TIP_25_GOALS            : tip25,
                CONST.TIP_35_GOALS            : tip35
            }
    
    return result

def getTips(hTeam,aTeam,dbData):
    goalsTips   = __getGoalsTipOfHomeTeamAwayTeamWithStats__(hTeam,aTeam,dbData)
    goalsTemp   = __getExpectedGoalsOfHomeTeamAwayTeamwithStats__(hTeam,aTeam,dbData)
    poissonTips = __possibleScoreForHomeExpectedGoalsAwayExpectedGoals__(goalsTemp[0], goalsTemp[1])
    result =    {
                    CONST.GOALS_TIPS                : goalsTips,
                    CONST.POISSON_TIPS              : poissonTips[0],
                    CONST.BIVARIATE_POISSON_TIPS    : poissonTips[1],
                }
    return result

if __name__ == '__main__':
    print ('\nThis is not a executable. Use the import to get the functions!!!\n')