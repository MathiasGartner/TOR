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

TIME_OFFSET_FOR_DISPLAY = "interval 2 hour"

cursor = db.cursor(named_tuple=True)

def executeQuery(query):
    cursor.execute(query)
    data = cursor.fetchall()
    return data

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
    query = "SELECT Id, IP, Material, Position, Latin, IsActive FROM client WHERE MAC = %(clientMAC)s"
    cursor.execute(query, { "clientMAC" : clientMAC })
    data = cursor.fetchone()
    if data is None:
        #raise Exception("Could not read client identity for: ", clientMAC)
        log.warning("Could not read client identity for: {}".format(clientMAC))
    return data

def getClientIdentityByClientId(clientId):
    query = "SELECT Id, IP, Material, Position, Latin, IsActive FROM client WHERE Id = %(id)s"
    cursor.execute(query, { "id" : clientId })
    data = cursor.fetchone()
    if data is None:
        #raise Exception("Could not read client identity for: ", clientMAC)
        log.warning("Could not read client identity for Id: {}".format(clientId))
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

def getBusyClients():
    query = "SELECT Id, Position, Latin FROM client WHERE IsActive = 1 AND CurrentState != 'WAITING'"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

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
    query = "INSERT INTO jobqueue (ClientId, JobCode, JobParameters) SELECT %(clientId)s As ClientId, IFNULL( (SELECT JobCode FROM jobqueue WHERE ClientId = %(clientId)s AND JobCode <> 'U' ORDER BY Id DESC LIMIT 1), 'W') AS JobCode, (SELECT JobParameters FROM jobqueue WHERE ClientId = %(clientId)s AND JobCode <> 'U' ORDER BY Id DESC LIMIT 1) AS JobParameters;"
    cursor.execute(query, {"clientId": clientId})

def setCurrentStateForUserMode(clientId, state):
    query = "UPDATE client SET CurrentState = %(state)s WHERE Id = %(clientId)s"
    cursor.execute(query, { "state": state, "clientId" : clientId })

def clearAllCurrentStates():
    query = "UPDATE client SET CurrentState = '', UserModeActive = 0"
    cursor.execute(query)

def setJobsByJobProgram(programName, startInNMinutes=0):
    query = "INSERT INTO jobqueue (ClientId, JobCode, JobParameters, ExecuteAt) SELECT ClientId, JobCode, JobParameters, Date_ADD(NOW(), INTERVAL %(minutes)s MINUTE) FROM jobprogram WHERE Name = %(programName)s"
    cursor.execute(query, { "programName": programName, "minutes": startInNMinutes })

def getAllClients(includeWihtoutPosition=False):
    query = "SELECT Id, IP, Material, Position, Latin, AllowUserMode, IsActive FROM client WHERE Position IS NOT NULL ORDER BY Position"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getAllAvailableClients():
    query = "SELECT Id, IP, Material, Position, Latin, AllowUserMode, IsActive FROM client WHERE IsAvailable = 1 ORDER BY Latin"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getAllPossibleClients():
    query = "SELECT Id, IP, Material, Position, Latin, AllowUserMode, IsActive FROM client ORDER BY Position"
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

def setClientPosition(clientId, position=None):
    query = "UPDATE client SET Position = %(position)s WHERE Id = %(clientId)s"
    cursor.execute(query, {"position": position, "clientId": clientId})

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

def getClientLog():
    query = "SELECT c.Position, c.Latin, l.MessageType AS Type, l.MessageCode, l.Message, DATE_ADD(Time, " + TIME_OFFSET_FOR_DISPLAY + ") AS Time FROM clientlog l LEFT JOIN client c ON c.Id = l.ClientId ORDER BY l.Id DESC LIMIT 100"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getClientLogByClientId(clientId):
    query = "SELECT MessageType AS Type, MessageCode, Message, DATE_ADD(Time, " + TIME_OFFSET_FOR_DISPLAY + ") AS Time FROM clientlog WHERE ClientId = %(clientId)s ORDER BY Id DESC LIMIT 1000"
    cursor.execute(query, {"clientId": clientId})
    data = cursor.fetchall()
    return data

def getRecentClientLogError(clientId):
    query = "SELECT Id, MessageCode, Message, Time FROM clientlog WHERE MessageType = 'ERROR' AND ClientId = %(clientId)s AND IsAcknowledged = 0 ORDER BY Time DESC LIMIT 1"
    cursor.execute(query, {"clientId": clientId})
    data = cursor.fetchone()
    return data

def acknowledgeErrorLog(logId):
    query = "UPDATE clientlog SET IsAcknowledged = 1 WHERE Id = %(logId)s"
    cursor.execute(query, {"logId": logId})

def getResults():
    query = "SELECT c.Position, c.Latin, Result, UserGenerated, X, Y, DATE_ADD(Time, " + TIME_OFFSET_FOR_DISPLAY + ") AS Time FROM diceresult d LEFT JOIN client c ON c.Id = d.ClientId ORDER BY d.Id DESC LIMIT 100"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getResultsByEvent(event):
    query = "SELECT c.Position, c.Latin, Result, UserGenerated, X, Y, DATE_ADD(Time, " + TIME_OFFSET_FOR_DISPLAY + ") AS Time FROM diceresult d LEFT JOIN client c ON c.Id = d.ClientId WHERE d.Source = %(event)s AND c.Position >=1 AND c.Position <= 27 ORDER BY d.Id DESC"
    cursor.execute(query, {"event": event})
    data = cursor.fetchall()
    return data

def getResultsByClientId(clientId):
    query = "SELECT Result, UserGenerated, X, Y, DATE_ADD(Time, " + TIME_OFFSET_FOR_DISPLAY + ") AS Time FROM diceresult WHERE ClientId = %(clientId)s ORDER BY Id DESC LIMIT 100"
    cursor.execute(query, {"clientId": clientId})
    data = cursor.fetchall()
    return data

def getAllClientResultContribution(lastNResults=100):
    query = "SELECT c.Id, IFNULL(contributions.Contribution, 0) AS Contribution, IFNULL(contributions.AverageResult, 0) AS AverageResult FROM client c LEFT JOIN (SELECT ClientId, COUNT(*) * 100 / %(lastNResults)s AS Contribution, AVG(Result) AS AverageResult FROM (SELECT ClientId, Result FROM diceresult ORDER BY ID DESC LIMIT %(lastNResults)s) as results GROUP BY ClientId) AS contributions ON c.Id = contributions.ClientId WHERE c.IsActive = 1"
    cursor.execute(query, {"lastNResults": lastNResults})
    data = cursor.fetchall()
    return data

def getResultStatisticForLastNHours(nHours):
    query = "SELECT COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE Time > DATE_ADD(NOW(), interval -%(nHours)s hour) GROUP BY ClientId"
    cursor.execute(query, {"nHours": nHours})
    data = cursor.fetchall()
    return data

def getResultStatisticForToday():
    query = "SELECT COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE DATE(Time) = CURDATE() GROUP BY ClientId"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def getResultStatisticForEvent(event):
    query = "SELECT COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE Source = %(event)s GROUP BY ClientId"
    cursor.execute(query, {"event": event})
    data = cursor.fetchall()
    return data

def getResultStatistics(event):
    query = """
        SELECT Position, Latin AS Name,
            IFNULL(twoHour.Count, 0) AS Count2Hours, IFNULL(twoHour.AverageResult, 0) AS Average2Hours,
            IFNULL(fourHour.Count, 0) AS Count4Hours, IFNULL(fourHour.AverageResult, 0) AS Average4Hours,
            IFNULL(today.Count, 0) AS CountToday, IFNULL(today.AverageResult, 0) AS AverageToday,
            IFNULL(event.Count, 0) AS CountEvent, IFNULL(event.AverageResult, 0) AS AverageEvent
        FROM client c
            LEFT JOIN (SELECT ClientId, COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE Time > DATE_ADD(NOW(), interval -2 hour) GROUP BY ClientId) twoHour ON twoHour.ClientId = c.Id
            LEFT JOIN (SELECT ClientId, COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE Time > DATE_ADD(NOW(), interval -4 hour) GROUP BY ClientId) fourHour ON fourHour.ClientId = c.Id
            LEFT JOIN (SELECT ClientId, COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE Date(Time) = CURDATE() GROUP BY ClientId) today ON today.ClientId = c.Id
            LEFT JOIN (SELECT ClientId, COUNT(*) AS Count, AVG(Result) AS AverageResult FROM diceresult WHERE Source = %(event)s GROUP BY ClientId) event ON event.ClientId = c.Id
        WHERE Position IS NOT NULL
        ORDER BY Count2Hours DESC
        """
    cursor.execute(query, {"event": event})
    data = cursor.fetchall()
    return data

