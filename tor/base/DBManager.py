import mysql.connector as mysql

import tor.TORSettingsPrivate as tsp

db = mysql.connect(
    host = tsp.DATABASE_HOST,
    user = tsp.DATABASE_USER,
    passwd = tsp.DATABASE_PASSWORD,
    database = "tor"
)

cursor = db.cursor(named_tuple=True)

def writeResult(clientId, result):
    query = "INSERT INTO diceresult (ClientId, Result) VALUES ({}, {})".format(clientId, result)
    cursor.execute(query)
    db.commit()

def getClientIdentity(clientName):
    query = "SELECT Id, IP, Name, Material FROM client WHERE Name = %(client_name)s"
    cursor.execute(query, { "client_name" : clientName })
    data = cursor.fetchone()
    if data is None:
        raise Exception("Could not read client identity for: ", clientName)
    return data