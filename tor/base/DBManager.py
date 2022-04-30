import logging
log = logging.getLogger(__name__)

import mysql.connector as mysql

import tor.TORSettings as ts
from tor.server.Job import Job

db = mysql.connect(
    host = ts.DB_HOST,
    user = ts.DB_USER,
    passwd = ts.DB_PASSWORD,
    database = "tor",
    autocommit = True
)

cursor = db.cursor(named_tuple=True)

def logClientAction(clientId, messageType, messageCode, message):
    query = "INSERT INTO clientlog (ClientId, MessageType, MessageCode, Message) VALUES (%s, %s, %s, %s)"
    data = (clientId, messageType, messageCode, message)
    cursor.execute(query, data)
    db.commit()

def getClientSettings(clientId):
    query = "SELECT Name, Value FROM clientsettings WHERE ClientId = %(clientId)s"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchall()
    return data

def saveClientSettings(clientId, settings):
    query = "INSERT INTO clientsettings (ClientId, Name, Value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Value = VALUES(Value)"
    data = [(clientId, s[0], str(s[1]) if type(s[1]) is list else s[1]) for s in settings]
    cursor.executemany(query, data)

def writeResult(clientId, result, x, y, userGenerated, source):
    query = "INSERT INTO diceresult (ClientId, Result, X, Y, UserGenerated, Source) VALUES (%s, %s, %s, %s, %s, %s)"
    data = (clientId, result, x, y, userGenerated, source)
    cursor.execute(query, data)
    db.commit()

def getClientIdentity(clientMAC):
    query = "SELECT Id, IP, Material, Position FROM client WHERE MAC = %(clientMAC)s"
    cursor.execute(query, { "clientMAC" : clientMAC })
    data = cursor.fetchone()
    if data is None:
        #raise Exception("Could not read client identity for: ", clientMAC)
        log.warning("Could not read client identity for: {}".format(clientMAC))
    return data

def getNextJobForClientId(clientId):
    query = "SELECT ClientId, JobCode, JobParameters, ExecuteAt FROM jobqueue WHERE ClientId = %(clientId)s ORDER BY Id DESC LIMIT 1"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchone()
    if data is None:
        data = Job()
        data.ClientId = clientId
        data.JobCode = "W"
        data.JobParameters = 5
        data.ExecuteAt = None
    return data

def getCurrentJobs():
    query = """ WITH ranked_jobs AS (
                    SELECT j.ClientId, j.JobCode, j.JobParameters, j.ExecuteAt, ROW_NUMBER() OVER (PARTITION BY ClientId ORDER BY id DESC) AS rj
                    FROM jobqueue AS j
                )
                SELECT c.Id, j.JobCode, j.JobParameters, j.ExecuteAt FROM ranked_jobs j LEFT JOIN client c ON c.ID = j.ClientId WHERE rj = 1 AND c.Position IS NOT NULL"""
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getMeshpoints(clientId):
    query = "SELECT Type, No, X, Y, Z FROM meshpoints WHERE ClientId = %(clientId)s ORDER BY Type, No"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchall()
    return data

def saveMeshpoints(clientId, type, points):
    query = "INSERT INTO meshpoints (ClientId, Type, No, X, Y, Z) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE X = VALUES(X), Y = VALUES(Y), Z = VALUES(Z)"
    data = [(clientId, type, i, p[0], p[1], p[2]) for (i, p) in enumerate(points)]
    cursor.executemany(query, data)

def saveJobs(jobs):
    if not isinstance(jobs, list):
        jobs = [jobs]
    query = "INSERT INTO jobqueue (ClientId, JobCode, JobParameters, ExecuteAt) VALUES (%s, %s, %s, %s)"
    data = [(j.ClientId, j.JobCode, j.JobParameters, j.ExecuteAt) for j in jobs]
    cursor.executemany(query, data)

def getIdByPosition(position):
    query = "SELECT Id FROM client WHERE Position = %(pos)s"
    cursor.execute(query, { "pos" : position })
    data = cursor.fetchone()
    return data[0]

def getIPByPosition(position):
    query = "SELECT IP FROM client WHERE Position = %(pos)s"
    cursor.execute(query, { "pos" : position })
    data = cursor.fetchone()
    return data[0]

def getUserAction(clientId, deleteAction=True):
    query = "SELECT Id, Action, Parameters FROM useraction WHERE ClientId = %(clientId)s ORDER BY Id DESC LIMIT 1"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchone()
    if data is not None:
        if deleteAction:
            query = "DELETE FROM useraction WHERE ClientId = %(clientId)s and Id <= %(id)s"
            cursor.execute(query, {"clientId": clientId, "id": data[0]})
        data = {"Action": data[1], "Parameters": data[2]}
    else:
        data = {"Action": "NONE", "Parameters": ""}
    return data

def exitUserMode(clientId):
    query = "UPDATE client SET CurrentState = '', UserModeActive = 0 WHERE Id = %(clientId)s"
    cursor.execute(query, {"clientId": clientId})
    #TODO: do not query same data twice (for JobCode and JobParameters)
    query = "INSERT INTO jobqueue (ClientId, JobCode, JobParameters) SELECT %(clientId)s As ClientId, IFNULL( (SELECT JobCode FROM jobqueue WHERE ClientId = %(clientId)s AND JobCode <> 'U' ORDER BY Id DESC LIMIT 1), 'W') AS JobCode, IFNULL( (SELECT JobParameters FROM jobqueue WHERE ClientId = %(clientId)s AND JobCode <> 'U' ORDER BY Id DESC LIMIT 1), 'W') AS JobParameters;"
    cursor.execute(query, {"clientId": clientId})

def setCurrentStateForUserMode(clientId, state):
    query = "UPDATE client SET CurrentState = %(state)s WHERE Id = %(clientId)s"
    cursor.execute(query, { "state": state, "clientId" : clientId })

def getAllClients():
    query = "SELECT Id, IP, Material, Position, Latin, AllowUserMode, IsActive FROM client WHERE Position IS NOT NULL ORDER BY Position"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getAllClientStatistics():
    query = """ WITH ranked_results AS (
                    SELECT d.ClientId, d.Result, ROW_NUMBER() OVER (PARTITION BY ClientId ORDER BY id DESC) AS rr
                    FROM diceresult AS d
                )
                SELECT c.Id, AVG(r.Result) AS ResultAverage, STDDEV(r.Result) AS ResultStddev FROM ranked_results r LEFT JOIN client c ON c.ID = r.ClientId WHERE rr < 100 AND c.Position IS NOT NULL GROUP BY r.ClientId"""
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def setUserModeEnabled(clientId, enabled):
    query = "UPDATE client SET AllowUserMode = %(userMode)s WHERE Id = %(clientId)s"
    cursor.execute(query, {"userMode": enabled, "clientId": clientId})

def setClientIsActive(clientId, active):
    query = "UPDATE client SET IsActive = %(active)s WHERE Id = %(clientId)s"
    cursor.execute(query, {"active": active, "clientId": clientId})

def getAllJobProgramNames():
    query = "SELECT DISTINCT Name FROM jobprogram"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getAllJobPrograms():
    query = "SELECT Name, ClientId, JobCode, JobParameters FROM jobprogram"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getJobsByProgramName(name):
    query = "SELECT ClientId AS Id, JobCode, JobParameters FROM jobprogram WHERE Name = %(name)s"
    cursor.execute(query, {"name": name})
    data = cursor.fetchall()
    return data
