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

def writeResult(clientId, result):
    query = "INSERT INTO diceresult (ClientId, Result) VALUES ({}, {})".format(clientId, result)
    cursor.execute(query)
    db.commit()

def getClientIdentity(clientMAC):
    query = "SELECT Id, IP, Name, Material, Position FROM client WHERE MAC = %(clientMAC)s"
    cursor.execute(query, { "clientMAC" : clientMAC })
    data = cursor.fetchone()
    if data is None:
        raise Exception("Could not read client identity for: ", clientMAC)
    return data

def getNextJobForClientId(clientId):
    query = "select j.Code, q.JobParameters FROM tor.jobqueue q LEFT JOIN tor.job j ON q.JobId = j.Id WHERE q.ClientId = %(clientId)s ORDER BY q.ExecuteAt, q.Id"
    cursor.execute(query, { "clientId" : clientId })
    data = cursor.fetchone()
    if data is None:
        data = Job()
        data.Code = "W"
        data.JobParameters = 1
    return data