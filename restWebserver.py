import cherrypy, json
import serverUtils
import serverConstants as CONST
import tips

class HOMESTATS(object):
    exposed = True
    def __init__(self):
        pass

    def POST(self):
        body = cherrypy.request.body.read()
        print ("HOMESTATS: " + body)
        
        if body in dbFile:
            outObject = dbFile[body][CONST.TEAM_HOME_STATS]
            return serverUtils.jsonExport(outObject)
        else:
            return serverUtils.jsonExport({'ERROR' : 'teams not found'})

    def GET(self):
        return methodNotAllowed()

    def PUT(self):
        return methodNotAllowed()

    def DELETE(self):
        return methodNotAllowed()

    def PATCH(self):
        return methodNotAllowed()

    # HTML5 
    # def OPTIONS(self):                                                      
    #     cherrypy.response.headers['Access-Control-Allow-Credentials'] = True
    #     cherrypy.response.headers['Access-Control-Allow-Origin'] = cherrypy.request.headers['ORIGIN']
    #     cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, DELETE'                                     
    #     cherrypy.response.headers['Access-Control-Allow-Headers'] = cherrypy.request.headers['ACCESS-CONTROL-REQUEST-HEADERS']

class AWAYSTATS(object):
    exposed = True
    def __init__(self):
        pass

    def POST(self):
        body = cherrypy.request.body.read()
        print ("AWAYSTATS: " + body)
        
        if body in dbFile:
            outObject = dbFile[body][CONST.TEAM_AWAY_STATS]
            return serverUtils.jsonExport(outObject)
        else:
            return serverUtils.jsonExport({'ERROR' : 'teams not found'})

    def GET(self):
        return methodNotAllowed()

    def PUT(self):
        return methodNotAllowed()

    def DELETE(self):
        return methodNotAllowed()

    def PATCH(self):
        return methodNotAllowed()

class TOTALSTATS(object):
    exposed = True
    def __init__(self):
        pass

    def POST(self):
        body = cherrypy.request.body.read()
        print ("TOTALSTATS: " + body)
        
        if body in dbFile:
            outObject = dbFile[body][CONST.TEAM_TOTAL_STATS]
            return serverUtils.jsonExport(outObject)
        else:
            return serverUtils.jsonExport({'ERROR' : 'teams not found'})

    def GET(self):
        return methodNotAllowed()

    def PUT(self):
        return methodNotAllowed()

    def DELETE(self):
        return methodNotAllowed()

    def PATCH(self):
        return methodNotAllowed()

class DUALSTATS(object):
    exposed = True
    def __init__(self):
        pass

    def POST(self):
        body = cherrypy.request.body.read()
        print ("DUALSTATS: " + body)

        obj_json = ''
        try:
            obj_json = json.loads(body)
        except:
            return wrongRequest()
        
        if len(obj_json) == 2:
            homestats = dbFile[obj_json[0]][CONST.TEAM_HOME_STATS]
            awaystats = dbFile[obj_json[1]][CONST.TEAM_AWAY_STATS]
            tipsStats = tips.getTips(obj_json[0], obj_json[1], dbFile)
            outObject = {
                            obj_json[0] : homestats,
                            obj_json[1] : awaystats,
                            "tips"      : tipsStats
                        }
            return serverUtils.jsonExport(outObject)
        else:
            return serverUtils.jsonExport({'ERROR' : 'only 2 teams allowed'})
            
    def GET(self):
        return methodNotAllowed()

    def PUT(self):
        return methodNotAllowed()

    def DELETE(self):
        return methodNotAllowed()

    def PATCH(self):
        return methodNotAllowed()

class UPDATE(object):
    exposed = True
    def POST(self):
        body = cherrypy.request.body.read()

        if body == 'updateFile':
            reloadFile()
            return serverUtils.jsonExport({'SUCCESS' : 'dbFile reloaded!'})
        else:
            return wrongRequest()

    def GET(self):
        return methodNotAllowed()

    def PUT(self):
        return methodNotAllowed()

    def DELETE(self):
        return methodNotAllowed()

    def PATCH(self):
        return methodNotAllowed()

class ROOT(object):
    exposed = True
    def POST(self):
        return methodNotAllowed()

    def GET(self):
        return methodNotAllowed()

    def PUT(self):
        return methodNotAllowed()

    def DELETE(self):
        return methodNotAllowed()

    def PATCH(self):
        return methodNotAllowed()




def methodNotAllowed():
    return serverUtils.jsonExport({'ERROR' : '405 Method Not Allowed'})
    pass

def wrongRequest():
    return serverUtils.jsonExport({'ERROR' : 'wrong API request'})
    pass

def reloadFile():
    return serverUtils.getDbFilefromDisk()
    pass



dbFile = reloadFile()





if __name__ == '__main__':
    root = ROOT()
    root.homestats  = HOMESTATS()
    root.awaystats  = AWAYSTATS()
    root.totalstats = TOTALSTATS()
    root.dualstats  = DUALSTATS()
    root.update     = UPDATE()
    
    userpassdict = {'user' : 'pass'}
                    
    checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userpassdict)
    
    conf = {
            'global': {
                'server.socket_host'            : '0.0.0.0',
                'server.socket_port'            : 443,
                'server.ssl_module'             : 'pyopenssl',
                'server.ssl_certificate'        : '/media/sf_Stats_Server_Files_Save/cert/restServer.crt',
                'server.ssl_private_key'        : '/media/sf_Stats_Server_Files_Save/cert/restServer.key',
                # 'server.ssl_certificate_chain'  : '/media/sf_Stats_Server_Files_Save/cert/restServer.cst',
                'tools.auth_basic.on'           : True,
                'tools.auth_basic.realm'        : 'earth',
                'tools.auth_basic.checkpassword': checkpassword
            },
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            }
    }
    cherrypy.quickstart(root, '/', conf)
