# coding=utf-8
import spynner
import json
from lxml import html
import serverConstants as CONST
import serverUtils

def mainUrlFromID(championshipID):
    url = "http://stats.betradar.com/s4/?clientid=271&language=en#2_1,3_48,22_3,5_%s,9_fixtures,231_full,23_1" % championshipID
    # print url
    return url

def matchUrlFromID(matchID):
    return "http://stats.betradar.com/s4/?clientid=271&language=en#2_1,3_30,22_1,5_8238,9_match,8_%s,178_2674,7_2538" % matchID
    pass

def getHtml(url):
    # print url

    browser = spynner.Browser(
    # debug_level=spynner.INFO
    )

    browser.load(url, load_timeout=121)
    
    pageHtml = browser.html
    browser.close()
    
    # print pageHtml.encode('utf-8')
    return pageHtml

def mainPageParse(pageHtml, championshipID):
    # print '####### Loading Main Page'
    tree = html.fromstring(pageHtml.encode('utf-8'))
    rounds = tree.xpath('//*[@class="normaltable fixtures"]/tbody')


    gameList = []
    for round in rounds:
        for game in round.xpath('./tr'):

            #event half time score
            htArr = game.xpath('./td[starts-with(@class,"p1")]/text()')
            ht = htArr[0] if len(htArr)>0 else ''
            #event full time score
            ftArr = game.xpath('./td[starts-with(@class,"nt ftx")]/text()')
            ft = ftArr[0] if len(ftArr)>0 else ''

            if ht == '' and ft == '':
                ftArr = game.xpath('./td[starts-with(@class,"nt ftx")]/abbr/text()')
                ft = ftArr[0] if len(ftArr)>0 else ''

            # test if the game is Postponed
            if ft == 'Postponed' or ht == 'Postponed':
                continue

            if ht == '' and ft != '':
                continue

            #event date
            dateArr = game.xpath('./td[@class="datetime"]/text()')
            date = dateArr[0] if len(dateArr)>0 else ''
            
            #event date to sort games
            dateSplit           = date.split(' ')
            dateStringArray     = dateSplit[0].split('/')
            timeStringArray     = dateSplit[1].split(':')
            minutes = int(timeStringArray[1])
            hours   = int(timeStringArray[0])
            day     = int(dateStringArray[0])
            month   = int(dateStringArray[1])
            year    = int(dateStringArray[2])
            gameDateToSort = (60 * minutes + 3600 * hours + 86400 * day + 2678400 * month + 32140800 * year)
            
            #event home team
            homeTeamArr = game.xpath('./td[@class="match"]/a/span/span[starts-with(@class,"home")]/text()')
            homeTeam = homeTeamArr[0].strip() if len(homeTeamArr)>0 else ''
            
            #event away team
            awayTeamArr = game.xpath('./td[@class="match"]/a/span/span[starts-with(@class,"away")]/text()')
            awayTeam = awayTeamArr[0].strip() if len(awayTeamArr)>0 else ''
            
            #event home team logo link
            homeTeamLogoArr = game.xpath('./td[@class="match"]/a/img[@class="home"]/@src')
            homeTeamLogo = ''.join(['http:', homeTeamLogoArr[0]]).replace('small', 'big') if len(homeTeamLogoArr)>0 else ''

            #event away team logo link
            awayTeamLogoArr = game.xpath('./td[@class="match"]/a/img[@class="away"]/@src')
            awayTeamLogo = ''.join(['http:', awayTeamLogoArr[0]]).replace('small', 'big') if len(awayTeamLogoArr)>0 else ''

            #event BF id
            matchIDArr = game.xpath('./td[@class="match"]/a/@href')
            matchIDStr = matchIDArr[0] if len(matchIDArr)>0 else ''
            matchID = matchIDStr.split(', ')[1] if len(matchIDStr.split(', '))==3 else ''


            # print '--------------------------------------------------------'
            # print 'matchID:', matchID
            # print 'date:', date
            # print 'match:', homeTeam, 'vs', awayTeam
            # print 'scores:', 'ht(', ht, ') ft(', ft ,')'
            # print 'homeLogo:', homeTeamLogo
            # print 'awayLogo:', awayTeamLogo

            matchDic = dict()
            matchDic.update({
                                CONST.GAME_ID                   : matchID,
                                CONST.GAME_CHAMPIONSHIP_ID      : championshipID,
                                CONST.GAME_AWAY_TEAM            : awayTeam,
                                CONST.GAME_DATE                 : date,
                                CONST.GAME_DATE_TO_SORT         : gameDateToSort,
                                # CONST.GAME_DETAILS            : {},
                                # CONST.GAME_EVENTS             : {},
                                CONST.GAME_FT_SCORE             : ft,
                                CONST.GAME_HOME_TEAM            : homeTeam,
                                CONST.GAME_HF_SCORE             : ht,
                                CONST.GAME_CHAMPIONSHIP_NAME    : serverUtils.getChampionshipsNameFromID(championshipID),
                                CONST.GAME_HOME_LOGO            : homeTeamLogo,  
                                CONST.GAME_AWAY_LOGO            : awayTeamLogo,
                                # CONST.GAME_INPLAY_STATS       : {},
                                # CONST.GAME_LINEUPS            : {},
                                # CONST.GAME_SUBSTITUTES        : {}
                            })
            gameList.append(matchDic)

            # matchUrl = matchUrlFromID(matchID)
            # pageHtml = getHtml(matchUrl)
            # gameDetails = matchPageParse(pageHtml)
            # gameDetails["details"].update({
            #                                 "homeLogoLink" : homeTeamLogo,
            #                                 "awayLogoLink" : awayTeamLogo
            #                                 })
            # fullGameDic = dict(matchDic,**gameDetails)
            # pprint(fullGameDic)
            # print matchID, gameDetails["details"]["stadium"]

            # break
        # break
    # pprint(gameList)
    return sorted(gameList, key=lambda k: k[CONST.GAME_DATE_TO_SORT])

def matchPageParse(pageHtml, matchID):
    def gameInfo(treeHtml):
        #Game info Table (Stadium, League, Attendance, Referee, Managers, Shirts)
        details = treeHtml.xpath('//*[@class="matchdetails header nozebra jerseybox"]/tbody')
        if len(details)>0:
            
            #Home Team Stadium
            stadiumArr = details[0].xpath('./tr/td[@class="date first"]/text()')
            stadiumString = stadiumArr[0] if len(stadiumArr)>0 else ''
            stadium = ', '.join([stadiumString.split(', ')[1], stadiumString.split(', ')[2]]) if len(stadiumString.split(', '))>2 else ''

            #Info League/Attendance/Referee
            infoArr = details[0].xpath('./tr/td[@class="description first"]/text()')
            attendance = ''
            referee = ''
            for i in xrange(0,len(infoArr)):
                tempInfo = infoArr[i].split(': ')
                if tempInfo[0] == 'Attendance':
                    attendance = tempInfo[1]
                elif tempInfo[0] == 'Referee':
                    referee = tempInfo[1]

                #Managers
                homeManager = details[0].xpath('./tr/td[@class="homemanager"]/text()')
                if len(homeManager) > 0:
                        homeManager = homeManager[0]
                else:
                        homeManager = ''
                awayManager = details[0].xpath('./tr/td[@class="awaymanager"]/text()')
                if len(awayManager) > 0:
                        awayManager = awayManager[0]
                else:
                        awayManager = ''

                #Shirts
                homeShirt = details[0].xpath('./tr/td[@class="homeshirt first"]/span/img/@src')
                if len(homeShirt) > 0:
                        homeShirt = 'http://stats.betradar.com/s4/' + homeShirt[0]
                        homeShirt = homeShirt.replace('medium', 'large')
                else:
                        homeShirt = ''
                awayShirt = details[0].xpath('./tr/td[@class="awayshirt last"]/span/img/@src')
                if len(awayShirt) > 0:
                        awayShirt = 'http://stats.betradar.com/s4/' + awayShirt[0]
                        awayShirt = awayShirt.replace('medium', 'large')
                else:
                        awayShirt = ''

                #Logos
                homeTeamLogo = details[0].xpath('./tr/td[contains(concat(" ", @class, " "), " hometeam ")]/a/span/img/@src')
                if len(homeTeamLogo) > 0:
                        homeTeamLogo = 'http:' + homeTeamLogo[0]
                        homeTeamLogo = homeTeamLogo.replace('medium', 'big')
                else:
                        homeTeamLogo = ''

                awayTeamLogo = details[0].xpath('./tr/td[contains(concat(" ", @class, " "), " awayteam ")]/a/span/img/@src')
                if len(awayTeamLogo) > 0:
                        awayTeamLogo = 'http:' + awayTeamLogo[0]
                        awayTeamLogo = awayTeamLogo.replace('medium', 'big')
                else:
                        awayTeamLogo = ''

        #Game info Table
        # print(type(stadium))
        # print stadium.encode('utf-8')
        # print 'stadium: '       , stadium.encode('utf-8')
        # print 'attendance: '    , attendance.encode('utf-8')
        # print 'referee: '       , referee.encode('utf-8')
        # print 'awayManager: '   , awayManager.encode('utf-8')
        # print 'homeManager: '   , homeManager.encode('utf-8')
        # print 'homeShirt: '     , homeShirt.encode('utf-8')
        # print 'awayShirt: '     , awayShirt.encode('utf-8')
        
        #game events
        return {    
                    CONST.GAME_ID       : matchID,
                    CONST.GAME_DETAILS  : {
                                            CONST.DETAILS_STADIUM         : stadium.encode('utf-8'),
                                            CONST.DETAILS_ATTENDANCE      : attendance.encode('utf-8'),
                                            CONST.DETAILS_REFEREE         : referee.encode('utf-8'),
                                            CONST.DETAILS_AWAY_MANAGER    : awayManager.encode('utf-8'),
                                            CONST.DETAILS_HOME_MANAGER    : homeManager.encode('utf-8'),
                                            CONST.DETAILS_HOME_SHIRT      : homeShirt.encode('utf-8'),
                                            CONST.DETAILS_AWAY_SHIRT      : awayShirt.encode('utf-8'),
                                            # CONST.DETAILS_HOME_LOGO       : homeTeamLogo.encode('utf-8'),
                                            # CONST.DETAILS_AWAY_LOGO       : awayTeamLogo.encode('utf-8')
                                        }
                }

    def gameEvents(treeHtml):
        #game events (goals/sustitutions/cads)
        events = treeHtml.xpath('//*[@class="matchdetails_events matchdetails events normaltable"]/tbody')
        '''
        Safari dev console:
        $x('//*[@class="matchdetails_events matchdetails events normaltable"]/tbody')
        '''

        homeCardsTemp           = []
        homeGoalsTemp           = []
        homeSubstitutionsTemp   = []
        awayCardsTemp           = []
        awayGoalsTemp           = []
        awaySubstitutionsTemp   = []
        goalsOrderTemp          = []

        if len(events)>0:
            eventsRows = events[0].xpath('./tr')
            for event in eventsRows:
                homeAwayTest = event.xpath('./td/@class')
                for test in homeAwayTest:
                    if test == 'player' or test == 'player last':
                        homeAwayTest = test
                        break


                normalTime = event.xpath('./td[@class="time"]/text()')[0].replace("'", "")
                injuryTime = event.xpath('./td[@class="injurytime"]/text()')
                if len(injuryTime)>0:
                    injuryTime = event.xpath('./td[@class="injurytime"]/text()')[0].replace("(", "").replace(")", "").replace(" ", "")
                else:
                    injuryTime = ""

                time = ''.join([normalTime, injuryTime]).strip()
                player = event.xpath('./td[starts-with(@class,"player")]/text()')[0]
                eventType = event.xpath('./td/@title')[0]

                if homeAwayTest == 'player': #Home events
                    if eventType == 'Substitution':
                        homeSubstitutionsTemp.append(
                            [
                                {
                                    CONST.EVENT_INJURY_TIME   : injuryTime,
                                    CONST.EVENT_NORMAL_TIME   : normalTime,
                                    CONST.EVENT_TIME          : time,
                                    CONST.EVENT_PLAYER        : player,
                                    CONST.EVENT_TYPE          : eventType
                                }
                            ])
                    elif eventType == 'Goal' or eventType == 'Own goal':
                        homeGoalsTemp.append(
                            [
                                {
                                    CONST.EVENT_INJURY_TIME   : injuryTime,
                                    CONST.EVENT_NORMAL_TIME   : normalTime,
                                    CONST.EVENT_TIME          : time,
                                    CONST.EVENT_PLAYER        : player,
                                    CONST.EVENT_TYPE          : eventType
                                }
                            ])
                        goalsOrderTemp.append("home")
                    elif eventType == 'Yellow card' or eventType == 'Yellow/red card' or eventType == 'Red card':
                        homeCardsTemp.append(
                            [
                                {
                                    CONST.EVENT_INJURY_TIME   : injuryTime,
                                    CONST.EVENT_NORMAL_TIME   : normalTime,
                                    CONST.EVENT_TIME          : time,
                                    CONST.EVENT_PLAYER        : player,
                                    CONST.EVENT_TYPE          : eventType
                                }
                            ])
                    else:
                        print ('---------------------------------------> event Type not known:', eventType)
                elif homeAwayTest == 'player last': #Away events
                    if eventType == 'Substitution':
                        awaySubstitutionsTemp.append(
                            [
                                {
                                    CONST.EVENT_INJURY_TIME   : injuryTime,
                                    CONST.EVENT_NORMAL_TIME   : normalTime,
                                    CONST.EVENT_TIME          : time,
                                    CONST.EVENT_PLAYER        : player,
                                    CONST.EVENT_TYPE          : eventType
                                }
                            ])
                    elif eventType == 'Goal' or eventType == 'Own goal':
                        awayGoalsTemp.append(
                            [
                                {
                                    CONST.EVENT_INJURY_TIME   : injuryTime,
                                    CONST.EVENT_NORMAL_TIME   : normalTime,
                                    CONST.EVENT_TIME          : time,
                                    CONST.EVENT_PLAYER        : player,
                                    CONST.EVENT_TYPE          : eventType
                                }
                            ])
                        goalsOrderTemp.append("away")
                    elif eventType == 'Yellow card' or eventType == 'Yellow/red card' or eventType == 'Red card':
                        awayCardsTemp.append(
                            [
                                {
                                    CONST.EVENT_INJURY_TIME   : injuryTime,
                                    CONST.EVENT_NORMAL_TIME   : normalTime,
                                    CONST.EVENT_TIME          : time,
                                    CONST.EVENT_PLAYER        : player,
                                    CONST.EVENT_TYPE          : eventType
                                }
                            ])
                    else:
                        print ('---------------------------------------> event Type not known:', eventType)

                # print '---------------------------'
                # print 'homeAwayTest:', homeAwayTest
                # print 'normalTime:', normalTime
                # print 'injuryTime:', injuryTime
                # print 'time:', time
                # print 'player:', player
                # print 'eventType:', eventType
 

        '''
        MISSING: 
        INGAME STATS    (class="matchdetails_details normaltable")
        LINEUPS         (class="matchdetails lineups normaltable")
        SUBSTITUTES     (class="matchdetails substitutes normaltable")
        '''

        #awayInplayStatsTemp     = []
        #homeInplayStatsTemp     = []
        awayLineUpsTemp         = []
        homeLineUpsTemp         = []
        awaySubstitutesTemp     = []
        homeSubstitutesTemp     = []

        #game inplayStats
        #eventsInplayStats = treeHtml.xpath('//*[@class="matchdetails_details normaltable"]/tbody')

        #game lineUps
        #eventsLineUps = treeHtml.xpath('//*[@class="matchdetails lineups normaltable"]/tbody')

        #game substitutes
        eventsSubstitutes = treeHtml.xpath('//*[@class="matchdetails substitutes normaltable"]/tbody')
        if len(eventsSubstitutes) > 0:
            eventsSubstitutesRows = eventsSubstitutes[0].xpath('./tr')
            for row in eventsSubstitutesRows:
                pass

        eventsReturn = {  
                            CONST.GAME_EVENTS: {
                                    CONST.EVENTS_HOME_TEAM : {
                                            CONST.EVENT_CARDS         : homeCardsTemp,
                                            CONST.EVENT_GOALS         : homeGoalsTemp,
                                            CONST.EVENT_SUBSTITUTIONS : homeSubstitutionsTemp
                                            },
                                    CONST.EVENTS_AWAY_TEAM : {
                                            CONST.EVENT_CARDS         : awayCardsTemp,
                                            CONST.EVENT_GOALS         : awayGoalsTemp,
                                            CONST.EVENT_SUBSTITUTIONS : awaySubstitutionsTemp
                                            },
                                    CONST.EVENTS_GOALS_ORDER  : goalsOrderTemp,
                                    CONST.GAME_INPLAY_STATS   : {
                                            CONST.INPLAY_STATS_AWAY   : {}, #awayInplayStatsTemp
                                            CONST.INPLAY_STATS_HOME   : {}  #homeInplayStatsTemp
                                            },
                                    CONST.GAME_LINEUPS    : {
                                            CONST.LINEUPS_STATS_AWAY  : awayLineUpsTemp,
                                            CONST.LINEUPS_STATS_HOME  : homeLineUpsTemp
                                            },
                                    CONST.GAME_SUBSTITUTES: {
                                            CONST.SUBSTITUTES_STATS_AWAY  : awaySubstitutesTemp,
                                            CONST.SUBSTITUTES_STATS_HOME  : homeSubstitutesTemp
                                            }
                                    }
                        }
        return eventsReturn

    # print '####### Loading Match Page'
    tree = html.fromstring(pageHtml.encode('utf-8'))
    gameInfoDic = gameInfo(tree)
    gameEvents = gameEvents(tree)
    gameDetailsDic = dict(gameInfoDic,**gameEvents)
    return gameDetailsDic

def gameListFromChampionshipID(championshipID):
    pageUrl = mainUrlFromID(championshipID) 
    pageHtml = getHtml(pageUrl)
    return mainPageParse(pageHtml, championshipID)

def gameInfoFromMatchID(matchID):
    matchUrl = matchUrlFromID(matchID)
    pageHtml = getHtml(matchUrl)
    gameDetails = matchPageParse(pageHtml, matchID)
    # fullGameDic = dict(matchDic,**gameDetails)
    return gameDetails

def getChampionshipFixtures(championshipID):
    championshipGameList = gameListFromChampionshipID(championshipID)
    fullGameArrayReturn = []
    gameNumber = 0
    gamesCount = len(championshipGameList)
    for game in championshipGameList:
        gameNumber += 1
        if game[CONST.GAME_FT_SCORE] == '':
            print ('({}/{}) ########## champ {}: id {} - SKIPPING'.format(gameNumber,gamesCount, game[CONST.GAME_CHAMPIONSHIP_ID], game[CONST.GAME_ID]))
            fullGameInfo = game
            # pprint(fullGameInfo)
            pass
        else:
            print ('({}/{}) id {} game {} vs {}'.format(gameNumber, gamesCount, game[CONST.GAME_ID], game[CONST.GAME_HOME_TEAM], game[CONST.GAME_AWAY_TEAM]))
            gameDetails = gameInfoFromMatchID(game[CONST.GAME_ID])
            fullGameInfo = dict(game,**gameDetails)
            pass

        fullGameArrayReturn.append(fullGameInfo)
    return fullGameArrayReturn


if __name__ == '__main__':
    print ('\nThis is not a executable. Use the import to get the functions!!!\n')
    import bfCrawler
    import inspect
    functs = inspect.getmembers(bfCrawler, inspect.isfunction)
    methods = [x[0] for x in functs]
    public = [i for i in methods if not i.startswith('_')]
    serverUtils.pprint(public)
    pass
