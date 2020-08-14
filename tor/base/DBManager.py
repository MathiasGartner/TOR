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

def getClientSettings(clientId):
    query = "SELECT Name, Value FROM clientsettings WHERE ClientId = %(clientId)s"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchall()
    return data

def saveClientSettings(clientId, settings):
    query = "INSERT INTO clientsettings (ClientId, Name, Value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Value = VALUES(Value)"
    data = [(clientId, s[0], str(s[1]) if type(s[1]) is list else s[1]) for s in settings]
    cursor.executemany(query, data)

def writeResult(clientId, result, x, y):
    query = "INSERT INTO diceresult (ClientId, Result, X, Y) VALUES (%s, %s, %s, %s)"
    data = (clientId, result, x, y)
    cursor.execute(query, data)
    db.commit()

def getClientIdentity(clientMAC):
    query = "SELECT Id, IP, Material, Position FROM client WHERE MAC = %(clientMAC)s"
    cursor.execute(query, { "clientMAC" : clientMAC })
    data = cursor.fetchone()
    if data is None:
        raise Exception("Could not read client identity for: ", clientMAC)
    return data

def getNextJobForClientId(clientId):
    query = "SELECT ClientId, JobCode, JobParameters, ExecuteAt FROM jobqueue WHERE ClientId = %(clientId)s ORDER BY ExecuteAt, Id"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchone()
    if data is None:
        data = Job()
        data.JobCode = "W"
        data.JobParameters = 5
        data.ExecuteAt = None
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